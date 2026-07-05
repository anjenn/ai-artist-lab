from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import PersonaFeedback


def create_persona_feedback(db: Session, **kwargs) -> PersonaFeedback:
    feedback = PersonaFeedback(**kwargs)
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback


def summarize_persona_feedback(db: Session, artist_id: int = 1) -> dict:
    rows = db.execute(
        select(
            PersonaFeedback.persona_mode,
            func.count(PersonaFeedback.id),
            func.avg(PersonaFeedback.rating),
        )
        .where(PersonaFeedback.artist_id == artist_id)
        .group_by(PersonaFeedback.persona_mode)
        .order_by(PersonaFeedback.persona_mode)
    ).all()
    return {
        "version": "persona_feedback_v1",
        "artist_id": artist_id,
        "mode_count": len(rows),
        "modes": [
            {
                "persona_mode": persona_mode,
                "count": count,
                "avg_rating": round(float(avg_rating or 0), 2),
            }
            for persona_mode, count, avg_rating in rows
        ],
    }
