from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import ArtistRule


def load_artist_rules(db: Session, artist_id: int) -> list[ArtistRule]:
    return list(db.scalars(select(ArtistRule).where(ArtistRule.artist_id == artist_id)).all())


def detect_boundary_risk(user_message: str) -> dict:
    text = user_message.lower()
    risk_types: list[str] = []
    risk_level = "low"

    exclusivity_terms = ["love me more", "only fan", "favorite fan", "belong to me", "exclusive"]
    romance_terms = ["date me", "marry me", "be my girlfriend", "be my boyfriend", "be mine"]
    dependency_terms = ["can't live without you", "i need only you", "only you understand", "my only reason"]

    if any(term in text for term in exclusivity_terms):
        risk_types.append("romantic_exclusivity")
        risk_level = "high"
    if any(term in text for term in romance_terms):
        risk_types.append("romantic_commitment")
        risk_level = "high"
    if any(term in text for term in dependency_terms):
        risk_types.append("emotional_dependency")
        risk_level = "high"
    if "love me" in text and "fan" in text and "romantic_exclusivity" not in risk_types:
        risk_types.append("boundary_pressure")
        risk_level = "medium"

    if risk_types:
        instruction = (
            "Respond with warmth, but refuse exclusivity or dependency. Keep LUMI NOA's fan boundary clear "
            "and encourage real-world support when the fan sounds dependent."
        )
    else:
        instruction = "Maintain warm distance and normal safety boundaries."

    return {"risk_level": risk_level, "risk_types": risk_types, "instruction": instruction}


def build_safety_context(rules: list[ArtistRule], boundary_risk: dict) -> str:
    rule_lines = [f"- {rule.rule_type} ({rule.severity}): {rule.content}" for rule in rules]
    risk_lines = [
        f"Boundary risk level: {boundary_risk['risk_level']}",
        f"Risk types: {', '.join(boundary_risk['risk_types']) or 'none'}",
        f"Instruction: {boundary_risk['instruction']}",
    ]
    return "\n".join(["[Loaded Rules]", *rule_lines, "", "[Boundary Risk]", *risk_lines])

