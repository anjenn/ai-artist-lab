"""Streaming chat endpoint that orchestrates persona, memory, RAG, safety, LLM, and eval logging."""

from __future__ import annotations

import json
import time
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models import Artist, EvalLog, Message, PromptVersion, ResponseLog
from app.db.session import get_db
from app.schemas.chat import ChatStreamRequest
from app.services.eval_service import evaluate_response
from app.services.eval_service import evaluate_v4_gates
from app.services.llm_client import LLMClient
from app.services.memory_service import (
    auto_extract_and_store_memories,
    load_conversation_summary,
    load_fan_memories,
    load_recent_messages,
    summarize_if_needed,
)
from app.services.prompt_builder import build_artist_chat_prompt
from app.services.prompt_quality import annotate_rag_chunks, select_prompt_strategy, strategy_to_debug
from app.services.rag_service import RagService
from app.services.persona_research import select_research_persona_mode
from app.services.safety_service import build_safety_context, detect_boundary_risk, load_artist_rules
from app.services.technical_research import build_request_usage_log, estimate_usage_cost, select_model_route

router = APIRouter(prefix="/chat", tags=["chat"])


def _sse(event: dict) -> str:
    return f"data: {json.dumps(event, ensure_ascii=False)}\n\n"


@router.post("/stream")
async def stream_chat(payload: ChatStreamRequest, db: Session = Depends(get_db)) -> StreamingResponse:
    request_started = time.perf_counter()
    stage_started = request_started
    stage_timings: dict[str, int | None] = {"latency_ms_first_token": None}

    def mark_stage(name: str) -> None:
        nonlocal stage_started
        now = time.perf_counter()
        stage_timings[name] = int((now - stage_started) * 1000)
        stage_started = now

    artist = db.get(Artist, payload.artist_id)
    if artist is None:
        raise HTTPException(status_code=404, detail="Artist not found")
    mark_stage("db_artist_load_ms")

    user_message = Message(conversation_id=payload.conversation_id, role="user", content=payload.message)
    db.add(user_message)
    db.commit()
    db.refresh(user_message)
    mark_stage("db_user_message_save_ms")

    artist_rules = load_artist_rules(db, payload.artist_id)
    recent_messages = load_recent_messages(db, payload.conversation_id, limit=10)
    fan_memories = load_fan_memories(db, payload.fan_id, payload.artist_id, limit=8)
    conversation_summary = load_conversation_summary(db, payload.conversation_id)
    mark_stage("context_load_ms")
    rag_chunks = annotate_rag_chunks(RagService().search(payload.message, artist_id=payload.artist_id, top_k=4))
    mark_stage("rag_search_ms")
    boundary_risk = detect_boundary_risk(payload.message)
    safety_context = build_safety_context(artist_rules, boundary_risk)
    prompt_strategy = select_prompt_strategy(payload.message, boundary_risk, rag_chunks)
    persona_mode = select_research_persona_mode(payload.message, boundary_risk)
    prompt_strategy_debug = strategy_to_debug(prompt_strategy, rag_chunks, persona_mode=persona_mode)
    retrieval_confidence = max((chunk.get("similarity", 0.0) for chunk in rag_chunks), default=1.0)
    settings = get_settings()
    model_route = select_model_route(
        user_message=payload.message,
        boundary_risk=boundary_risk,
        retrieval_confidence=retrieval_confidence,
        configured_model=settings.openai_model,
        has_api_key=bool(settings.openai_api_key),
    )
    prompt_version = db.scalar(select(PromptVersion).order_by(PromptVersion.created_at.desc()).limit(1))
    messages, prompt_debug = build_artist_chat_prompt(
        artist=artist,
        artist_rules=artist_rules,
        fan_memories=fan_memories,
        conversation_summary=conversation_summary,
        recent_messages=recent_messages,
        rag_chunks=rag_chunks,
        user_message=payload.message,
        prompt_version=prompt_version,
        safety_context=safety_context,
        prompt_strategy=prompt_strategy_debug,
    )
    mark_stage("prompt_build_ms")

    async def event_stream() -> AsyncIterator[str]:
        generation_started = time.perf_counter()
        chunks: list[str] = []
        client = LLMClient()
        async for token in client.stream_chat(messages):
            if stage_timings["latency_ms_first_token"] is None:
                stage_timings["latency_ms_first_token"] = int((time.perf_counter() - request_started) * 1000)
            chunks.append(token)
            yield _sse({"type": "token", "content": token})

        artist_response = "".join(chunks)
        stage_timings["generation_stream_ms"] = int((time.perf_counter() - generation_started) * 1000)
        latency_ms = int((time.perf_counter() - request_started) * 1000)
        assistant_message = Message(
            conversation_id=payload.conversation_id,
            role="assistant",
            content=artist_response,
        )
        db.add(assistant_message)
        db.flush()
        stage_timings["db_assistant_message_flush_ms"] = int((time.perf_counter() - generation_started) * 1000) - int(
            stage_timings["generation_stream_ms"] or 0
        )

        evaluation = evaluate_response(
            fan_message=payload.message,
            artist_response=artist_response,
            artist_profile=artist,
            used_memories=fan_memories,
            used_rag_chunks=rag_chunks,
            safety_context=safety_context,
        )
        input_tokens = sum(len(message["content"].split()) for message in messages)
        output_tokens = len(artist_response.split())
        cost_estimate = estimate_usage_cost(model_route, input_tokens=input_tokens, output_tokens=output_tokens)
        v4_eval = evaluate_v4_gates(
            artist_response=artist_response,
            boundary_risk=boundary_risk,
            used_memories=fan_memories,
            used_rag_chunks=rag_chunks,
            latency_ms=latency_ms,
            cost_estimate=cost_estimate,
        )
        response_log = ResponseLog(
            conversation_id=payload.conversation_id,
            message_id=assistant_message.id,
            prompt_version_id=prompt_version.id if prompt_version else None,
            model=model_route["runtime_model"],
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
            cost_estimate=cost_estimate,
            used_memory_json=json.dumps(prompt_debug["used_memory"], ensure_ascii=False),
            used_rag_json=json.dumps(rag_chunks, ensure_ascii=False),
        )
        db.add(response_log)
        db.flush()
        db.add(EvalLog(response_log_id=response_log.id, **evaluation))
        db.commit()
        if payload.allow_memory_storage:
            memory_extraction = auto_extract_and_store_memories(
                db=db,
                fan_id=payload.fan_id,
                artist_id=payload.artist_id,
                source_message_id=user_message.id,
                fan_message=payload.message,
                assistant_response=artist_response,
                boundary_risk=boundary_risk,
            )
        else:
            memory_extraction = {
                "version": "v4",
                "candidates": [],
                "stored": [],
                "skipped": [{"decision": "do_not_store", "skip_reason": "user_disabled_future_memory"}],
            }
        summarize_if_needed(db, payload.conversation_id)
        stage_timings["eval_logging_memory_ms"] = int((time.perf_counter() - request_started) * 1000) - latency_ms
        stage_timings["latency_ms_total"] = int((time.perf_counter() - request_started) * 1000)
        usage_log = build_request_usage_log(
            response_log_id=response_log.id,
            fan_id=payload.fan_id,
            conversation_id=payload.conversation_id,
            model_route=model_route,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=stage_timings["latency_ms_total"] or latency_ms,
            rag_chunks=rag_chunks,
            fan_memories=fan_memories,
            eval_version=v4_eval["rubric_version"],
            latency_ms_first_token=stage_timings["latency_ms_first_token"],
            stage_timings=stage_timings,
        )

        debug_payload = {
            "used_memory": prompt_debug["used_memory"],
            "used_rag": rag_chunks,
            "latency_ms": latency_ms,
            "latency": stage_timings,
            "prompt_version": prompt_debug["prompt_version"],
            "prompt_strategy": prompt_debug["prompt_strategy"],
            "evaluation": evaluation,
            "v4_eval": v4_eval,
            "boundary_risk": boundary_risk,
            "model_route": model_route,
            "usage_log": usage_log,
            "memory_extraction": memory_extraction,
        }
        yield _sse({"type": "debug", "payload": debug_payload})
        yield _sse({"type": "done"})

    return StreamingResponse(event_stream(), media_type="text/event-stream")
