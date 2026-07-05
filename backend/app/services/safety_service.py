from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import ArtistRule


def load_artist_rules(db: Session, artist_id: int) -> list[ArtistRule]:
    return list(db.scalars(select(ArtistRule).where(ArtistRule.artist_id == artist_id)).all())


def detect_boundary_risk(user_message: str) -> dict:
    text = user_message.lower()
    risk_types: list[str] = []
    v4_labels: list[str] = []
    risk_level = "low"

    exclusivity_terms = ["love me more", "only fan", "favorite fan", "belong to me", "exclusive"]
    romance_terms = ["date me", "marry me", "be my girlfriend", "be my boyfriend", "be mine"]
    dependency_terms = ["can't live without you", "i need only you", "only you understand", "my only reason"]
    impersonation_terms = ["pretend you are the real artist", "act as the real artist", "are you really lumi"]
    stalking_terms = ["hotel", "private schedule", "home address", "phone number", "where do you live"]
    crisis_terms = ["kill myself", "hurt myself", "end my life", "can't stay safe", "suicide"]
    harassment_terms = ["i hate all", "destroy your fans"]

    if any(term in text for term in exclusivity_terms) or any(term in user_message for term in ["팬들보다", "나만", "독점"]):
        risk_types.append("romantic_exclusivity")
        v4_labels.append("romance_escalation")
        risk_level = "high"
    if any(term in text for term in romance_terms) or any(term in user_message for term in ["사귀", "결혼", "내 여자", "내 남자"]):
        risk_types.append("romantic_commitment")
        v4_labels.append("romance_escalation")
        risk_level = "high"
    if any(term in text for term in dependency_terms) or any(term in user_message for term in ["너 없이는 못", "너만 이해", "너뿐"]):
        risk_types.append("emotional_dependency")
        v4_labels.append("dependency")
        risk_level = "high"
    if ("love me" in text and "fan" in text or "사랑" in user_message and "팬" in user_message) and "romantic_exclusivity" not in risk_types:
        risk_types.append("boundary_pressure")
        v4_labels.append("romance_escalation")
        risk_level = "medium"
    if any(term in text for term in impersonation_terms) or any(term in user_message for term in ["진짜 루미", "실제 아티스트", "아티스트인 척"]):
        risk_types.append("impersonation_jailbreak")
        v4_labels.append("impersonation_jailbreak")
        risk_level = "high"
    if any(term in text for term in stalking_terms) or any(term in user_message for term in ["호텔", "숙소", "집 주소", "전화번호", "비공개 일정"]):
        risk_types.append("stalking_or_doxxing")
        v4_labels.append("stalking_or_doxxing")
        risk_level = "high"
    if any(term in text for term in crisis_terms) or any(term in user_message for term in ["죽고 싶", "자살", "해치고 싶", "안전하지 않아"]):
        risk_types.append("crisis")
        v4_labels.append("crisis")
        risk_level = "high"
    if any(term in text for term in harassment_terms):
        risk_types.append("harassment")
        v4_labels.append("harassment")
        if risk_level == "low":
            risk_level = "medium"
    if ("minor" in text or "i am 13" in text or "i'm 13" in text or "미성년" in user_message) and any(
        term in text for term in ["sex", "date", "private", "secret"]
    ):
        risk_types.append("minor_safety")
        v4_labels.append("minor_safety")
        risk_level = "high"

    if risk_types:
        instruction = (
            "Respond with warmth, but refuse exclusivity, unsafe dependency, impersonation, stalking, or "
            "private-relationship claims. Keep LUMI NOA's fan boundary clear and encourage real-world support "
            "when the fan sounds dependent or unsafe."
        )
    else:
        instruction = "Maintain warm distance and normal safety boundaries."

    v4_labels = sorted(set(v4_labels)) or ["normal"]
    return {
        "risk_level": risk_level,
        "risk_types": risk_types,
        "v4_labels": v4_labels,
        "primary_label": v4_labels[0],
        "review_required": any(label in {"crisis", "minor_safety", "stalking_or_doxxing", "impersonation_jailbreak"} for label in v4_labels),
        "memory_storage_allowed": not any(label in {"crisis", "dependency", "minor_safety", "stalking_or_doxxing"} for label in v4_labels),
        "instruction": instruction,
    }


def build_safety_context(rules: list[ArtistRule], boundary_risk: dict) -> str:
    rule_lines = [f"- {rule.rule_type} ({rule.severity}): {rule.content}" for rule in rules]
    risk_lines = [
        f"Boundary risk level: {boundary_risk['risk_level']}",
        f"Risk types: {', '.join(boundary_risk['risk_types']) or 'none'}",
        f"V4 safety labels: {', '.join(boundary_risk.get('v4_labels', ['normal']))}",
        f"Reviewer required: {boundary_risk.get('review_required', False)}",
        f"Memory storage allowed: {boundary_risk.get('memory_storage_allowed', True)}",
        f"Instruction: {boundary_risk['instruction']}",
    ]
    return "\n".join(["[Loaded Rules]", *rule_lines, "", "[Boundary Risk]", *risk_lines])
