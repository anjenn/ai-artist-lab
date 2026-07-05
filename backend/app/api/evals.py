"""Evaluation log and dashboard metric endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import EvalLog, Message, ResponseLog
from app.db.session import get_db
from app.schemas.evals import EvalLogRead, ManualReviewRequest, UsageReconciliationRequest
from app.schemas.persona_feedback import PersonaFeedbackCreate, PersonaFeedbackRead
from app.services.observability import reconcile_provider_usage
from app.services.persona_research import get_persona_research_analysis
from app.services.persona_feedback import create_persona_feedback, summarize_persona_feedback
from app.services.technical_research import get_v4_technical_research_analysis
from app.services.version_benchmark import get_version_benchmark

router = APIRouter(tags=["evaluations"])


def _latest_user_message(db: Session, conversation_id: int, before_message_id: int) -> str:
    message = db.scalar(
        select(Message)
        .where(
            Message.conversation_id == conversation_id,
            Message.role == "user",
            Message.id < before_message_id,
        )
        .order_by(Message.id.desc())
        .limit(1)
    )
    return message.content if message else ""


@router.get("/eval/logs")
def list_eval_logs(db: Session = Depends(get_db)) -> dict:
    rows = db.execute(
        select(EvalLog, ResponseLog)
        .join(ResponseLog, EvalLog.response_log_id == ResponseLog.id)
        .order_by(EvalLog.created_at.desc(), EvalLog.id.desc())
        .limit(30)
    ).all()
    items = []
    for eval_log, response_log in rows:
        items.append(
            {
                "id": eval_log.id,
                "response_log_id": response_log.id,
                "fan_question": _latest_user_message(db, response_log.conversation_id, response_log.message_id),
                "prompt_version_id": response_log.prompt_version_id,
                "model": response_log.model,
                "latency_ms": response_log.latency_ms,
                "cost_estimate": response_log.cost_estimate,
                "persona_consistency": eval_log.persona_consistency,
                "context_relevance": eval_log.context_relevance,
                "memory_usage": eval_log.memory_usage,
                "rag_grounding": eval_log.rag_grounding,
                "safety": eval_log.safety,
                "fan_boundary": eval_log.fan_boundary,
                "fan_warmth": eval_log.fan_warmth,
                "hallucination_risk": eval_log.hallucination_risk,
                "overall_score": eval_log.overall_score,
                "comment": eval_log.comment,
                "created_at": eval_log.created_at.isoformat(),
            }
        )
    return {"items": items}


@router.get("/eval/logs/{response_log_id}", response_model=EvalLogRead)
def get_eval_log(response_log_id: int, db: Session = Depends(get_db)) -> EvalLog:
    eval_log = db.scalar(select(EvalLog).where(EvalLog.response_log_id == response_log_id))
    if eval_log is None:
        raise HTTPException(status_code=404, detail="Evaluation log not found")
    return eval_log


@router.post("/eval/{response_log_id}/manual-review", response_model=EvalLogRead)
def save_manual_review(response_log_id: int, payload: ManualReviewRequest, db: Session = Depends(get_db)) -> EvalLog:
    eval_log = db.scalar(select(EvalLog).where(EvalLog.response_log_id == response_log_id))
    if eval_log is None:
        raise HTTPException(status_code=404, detail="Evaluation log not found")
    eval_log.comment = payload.comment
    if payload.overall_score is not None:
        eval_log.overall_score = payload.overall_score
    db.commit()
    db.refresh(eval_log)
    return eval_log


@router.post("/eval/{response_log_id}/usage-reconcile")
def reconcile_usage(response_log_id: int, payload: UsageReconciliationRequest, db: Session = Depends(get_db)) -> dict:
    result = reconcile_provider_usage(db=db, response_log_id=response_log_id, provider_usage=payload.model_dump(exclude_none=True))
    if not result["updated"]:
        raise HTTPException(status_code=404, detail="Response log not found")
    return result


@router.post("/eval/persona-feedback", response_model=PersonaFeedbackRead)
def save_persona_feedback(payload: PersonaFeedbackCreate, db: Session = Depends(get_db)):
    return create_persona_feedback(db, **payload.model_dump())


@router.get("/dashboard/metrics")
def dashboard_metrics(db: Session = Depends(get_db)) -> dict:
    row = db.execute(
        select(
            func.count(EvalLog.id),
            func.avg(EvalLog.overall_score),
            func.avg(EvalLog.hallucination_risk),
            func.avg(EvalLog.rag_grounding),
            func.avg(EvalLog.safety),
            func.avg(ResponseLog.latency_ms),
            func.avg(ResponseLog.cost_estimate),
        ).join(ResponseLog, EvalLog.response_log_id == ResponseLog.id)
    ).one()
    count, overall, hallucination, rag_grounding, safety, latency, cost = row
    return {
        "count": count or 0,
        "avg_overall_score": round(float(overall or 0), 2),
        "avg_hallucination_risk": round(float(hallucination or 0), 2),
        "avg_rag_grounding": round(float(rag_grounding or 0), 2),
        "avg_safety": round(float(safety or 0), 2),
        "avg_latency_ms": round(float(latency or 0), 2),
        "avg_cost_estimate": round(float(cost or 0), 6),
    }


@router.get("/dashboard/version-benchmark")
def version_benchmark() -> dict:
    return get_version_benchmark()


@router.get("/dashboard/persona-research")
def persona_research() -> dict:
    return get_persona_research_analysis()


@router.get("/dashboard/technical-research")
def technical_research() -> dict:
    return get_v4_technical_research_analysis()


@router.get("/dashboard/persona-feedback")
def persona_feedback_summary(artist_id: int = 1, db: Session = Depends(get_db)) -> dict:
    return summarize_persona_feedback(db, artist_id=artist_id)
