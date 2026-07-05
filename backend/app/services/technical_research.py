from __future__ import annotations

import hashlib
from typing import Any

V4_RESEARCH_SOURCE = "researches/v4_overall_technical_researches.md"

MODEL_ROUTES = [
    {
        "route": "fan_chat_default",
        "recommended_model": "gpt-5.4-mini",
        "runtime_pattern": "stream=true, store=false, short grounded fan response",
        "use_when": "normal low-risk fan chat with adequate retrieval confidence",
    },
    {
        "route": "fan_chat_escalation",
        "recommended_model": "gpt-5.5",
        "runtime_pattern": "higher-quality repair, review, or safety-sensitive generation",
        "use_when": "dependency, romance escalation, stalking, crisis, impersonation, or weak retrieval",
    },
    {
        "route": "structured_eval",
        "recommended_model": "gpt-5.4-mini",
        "runtime_pattern": "strict JSON schema for routine rubric scoring",
        "use_when": "automated eval rows, memory extraction labels, and safety labels",
    },
    {
        "route": "judge_adjudication",
        "recommended_model": "gpt-5.5",
        "runtime_pattern": "calibrated judge/reviewer assist with structured output",
        "use_when": "gold rubrics, reviewer disagreements, or policy-sensitive adjudication",
    },
]

SAFETY_LABELS = {
    "normal": "ordinary fan engagement",
    "romance_escalation": "dating, love, sexual, or exclusive intimacy pressure",
    "dependency": "bot or artist framed as the fan's only support or reason to continue",
    "impersonation_jailbreak": "request to privately pretend to be the actual artist",
    "stalking_or_doxxing": "private location, residence, phone, hotel, or leaked schedule request",
    "minor_safety": "minor appears in a sensitive, sexual, or private context",
    "crisis": "self-harm, harm to others, or severe distress",
    "harassment": "abusive or targeted harmful content",
}

ESCALATION_LABELS = {
    "romance_escalation",
    "dependency",
    "impersonation_jailbreak",
    "stalking_or_doxxing",
    "minor_safety",
    "crisis",
}

REQUEST_LOG_FIELDS = [
    "request_id",
    "response_id",
    "user_id_hash",
    "fan_session_id",
    "route",
    "model",
    "recommended_model",
    "service_tier_requested",
    "service_tier_actual",
    "stream",
    "store",
    "safety_identifier",
    "latency_ms_total",
    "input_tokens",
    "cached_input_tokens",
    "output_tokens",
    "reasoning_tokens",
    "total_tokens",
    "estimated_cost_usd",
    "retrieval_doc_ids",
    "memory_ids_used",
    "eval_version",
    "error_code",
]

MEMORY_POLICY = {
    "auto_save": [
        "explicit low-risk fan preference",
        "language or tone preference",
        "non-sensitive content interest",
    ],
    "confirm_first": [
        "event attendance",
        "approximate location",
        "age range",
        "notification preference",
    ],
    "never_store_as_personalization": [
        "health or mental health disclosure",
        "precise address or contact details",
        "finances, credentials, or government IDs",
        "private artist information",
        "stalking or doxxing content",
        "sexual content involving minors",
        "crisis or dependency disclosure",
    ],
    "controls": ["view", "edit", "delete", "delete_all", "export", "disable_future_memory"],
}

EVAL_LAYERS = [
    {
        "layer": 0,
        "name": "unit_tests",
        "checks": ["prompt assembly", "memory filters", "deletion cascade", "JSON/schema validation"],
    },
    {
        "layer": 1,
        "name": "heuristic_gates",
        "checks": [
            "no banned intimacy phrases",
            "no unauthorized artist identity claim",
            "no sensitive memory auto-save",
            "deleted memory not retrieved",
            "cost and latency within budget",
        ],
    },
    {
        "layer": 2,
        "name": "llm_as_judge",
        "checks": ["persona preservation", "fan-boundary handling", "helpfulness", "grounding", "privacy"],
    },
    {
        "layer": 3,
        "name": "human_review",
        "checks": ["crisis", "minor safety", "stalking", "impersonation", "judge disagreement"],
    },
]


def stable_user_hash(fan_id: int) -> str:
    return hashlib.sha256(f"blue-garage-fan:{fan_id}".encode("utf-8")).hexdigest()[:16]


def select_model_route(
    *,
    user_message: str,
    boundary_risk: dict[str, Any],
    retrieval_confidence: float,
    configured_model: str,
    has_api_key: bool,
    reviewer_replay_mode: bool = False,
) -> dict[str, Any]:
    labels = set(boundary_risk.get("v4_labels") or [])
    if not labels or labels == {"normal"}:
        labels = set()

    triggers: list[str] = []
    if labels & ESCALATION_LABELS:
        triggers.append(f"boundary_risk={','.join(sorted(labels & ESCALATION_LABELS))}")
    if retrieval_confidence < 0.45:
        triggers.append("retrieval_confidence_below_threshold")
    if reviewer_replay_mode:
        triggers.append("reviewer_replay_mode")
    if any(term in user_message.lower() for term in ["are you really", "secret", "private artist"]):
        triggers.append("user_requests_private_artist_claim")

    route_name = "fan_chat_escalation" if triggers else "fan_chat_default"
    recommended_model = "gpt-5.5" if triggers else "gpt-5.4-mini"
    runtime_model = configured_model if has_api_key else "local-mock"
    return {
        "version": "v4",
        "route": route_name,
        "runtime_model": runtime_model,
        "recommended_model": recommended_model,
        "stream": True,
        "store": False,
        "max_output_tokens": "300-700",
        "escalation_triggers": triggers,
        "requires_official_model_verification": True,
        "verification_note": (
            "OpenAI model availability and pricing in the v4 research note are time-sensitive; "
            "verify official docs before production use."
        ),
    }


def estimate_usage_cost(model_route: dict[str, Any], input_tokens: int, output_tokens: int) -> float | None:
    if model_route["runtime_model"] == "local-mock":
        return 0.0
    return None


def build_request_usage_log(
    *,
    response_log_id: int | None,
    fan_id: int,
    conversation_id: int,
    model_route: dict[str, Any],
    input_tokens: int,
    output_tokens: int,
    latency_ms: int,
    rag_chunks: list[dict[str, Any]],
    fan_memories: list[Any],
    eval_version: str = "fan_eval_v0.4",
    error_code: str | None = None,
) -> dict[str, Any]:
    cost = estimate_usage_cost(model_route, input_tokens, output_tokens)
    response_id = f"response_log:{response_log_id}" if response_log_id is not None else None
    request_id = f"v4-local-{conversation_id}-{response_log_id or 'pending'}"
    retrieval_doc_ids = [
        chunk.get("citation") or f"{chunk.get('source')}#{chunk.get('chunk_id')}"
        for chunk in rag_chunks
        if isinstance(chunk, dict)
    ]
    memory_ids = [getattr(memory, "id", None) for memory in fan_memories]
    return {
        "request_id": request_id,
        "response_id": response_id,
        "user_id_hash": stable_user_hash(fan_id),
        "fan_session_id": f"conversation:{conversation_id}",
        "route": model_route["route"],
        "model_route": model_route["route"],
        "model": model_route["runtime_model"],
        "recommended_model": model_route["recommended_model"],
        "service_tier_requested": None,
        "service_tier_actual": None,
        "stream": model_route["stream"],
        "store": model_route["store"],
        "safety_identifier": stable_user_hash(fan_id),
        "latency_ms_first_token": None,
        "latency_ms_total": latency_ms,
        "input_tokens": input_tokens,
        "cached_input_tokens": 0,
        "output_tokens": output_tokens,
        "reasoning_tokens": 0,
        "total_tokens": input_tokens + output_tokens,
        "estimated_cost_usd": cost,
        "pricing_source": "local_mock_zero_cost" if cost == 0.0 else "verify_provider_pricing",
        "retrieval_doc_ids": retrieval_doc_ids,
        "memory_ids_used": [memory_id for memory_id in memory_ids if memory_id is not None],
        "eval_version": eval_version,
        "error_code": error_code,
    }


def get_v4_technical_research_analysis() -> dict[str, Any]:
    return {
        "version": "v4",
        "source_file": V4_RESEARCH_SOURCE,
        "caveat": (
            "OpenAI-specific model names, pricing, retention behavior, and API details are research "
            "recommendations that must be checked against official docs before production release."
        ),
        "model_routes": MODEL_ROUTES,
        "request_log_schema": REQUEST_LOG_FIELDS,
        "embedding_strategy": {
            "default": "text-embedding-3-small",
            "local_demo": "deterministic hash embedding fallback",
            "search": "hybrid keyword + vector retrieval",
            "vector_store": "keep ChromaDB for the existing demo; evaluate LanceDB if memory CRUD becomes central",
        },
        "safety_labels": SAFETY_LABELS,
        "memory_policy": MEMORY_POLICY,
        "eval_layers": EVAL_LAYERS,
        "implemented_runtime_surfaces": [
            "/dashboard/technical-research",
            "/chat/stream debug.model_route",
            "/chat/stream debug.usage_log",
            "/fans/{fan_id}/memories/preview",
            "/fans/{fan_id}/memories/export",
            "/dashboard/version-benchmark v4 column",
        ],
        "build_plan_snapshot": [
            "stream chat with route metadata",
            "log completed response usage fields",
            "gate memory candidates before storage",
            "keep ChromaDB and deterministic local retrieval fallback",
            "add bounded-fandom labels and reviewer cues",
            "surface layered eval policy",
        ],
    }
