from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class BenchmarkMetric:
    metric: str
    unit: str
    v1: int
    v2: int
    v3: int
    v4: int
    delta: int
    improvement_pct: float | None
    evidence: str


def _metric(metric: str, unit: str, v1: int, v2: int, v3: int, v4: int, evidence: str) -> BenchmarkMetric:
    delta = v4 - v3
    improvement_pct = round((delta / v3) * 100, 1) if v3 else None
    return BenchmarkMetric(
        metric=metric,
        unit=unit,
        v1=v1,
        v2=v2,
        v3=v3,
        v4=v4,
        delta=delta,
        improvement_pct=improvement_pct,
        evidence=evidence,
    )


def get_version_benchmark() -> dict:
    metrics = [
        _metric(
            "Automated regression tests",
            "tests",
            9,
            20,
            25,
            35,
            "pytest service suite: v1 baseline, v2 localization, v3 persona research, v4 technical policy tests",
        ),
        _metric(
            "Prompt strategy metadata",
            "fields",
            0,
            6,
            7,
            10,
            "strategy name, task type, techniques, output contract, quality checks, trust boundary, persona_mode, model_route, usage_log, v4_eval",
        ),
        _metric(
            "RAG provenance metadata",
            "fields/chunk",
            2,
            6,
            6,
            6,
            "source, chunk_id, citation, content_role, trust_level, injection_risk",
        ),
        _metric(
            "Prompt security guardrails",
            "checks",
            2,
            5,
            6,
            10,
            "safety rules, boundary risk, untrusted-context rule, injection patterns, risk logging, manner memory privacy, v4 labels, review cues, storage gate, cost/latency gate",
        ),
        _metric(
            "Korean intent coverage",
            "routes",
            0,
            4,
            7,
            10,
            "debut/lore, exam memory, fan-boundary safety, persona, support, research, RAG, prompt-security, privacy, deletion terms",
        ),
        _metric(
            "Prompt quality artifacts",
            "files",
            0,
            9,
            11,
            14,
            "prompts/*, evals/*, docs/*, knowledge_base/*, researches/* plus v4 technical research and KB artifacts",
        ),
        _metric(
            "Frontend language modes",
            "modes",
            1,
            2,
            2,
            2,
            "English-only v1 vs English/Korean top-nav switch",
        ),
        _metric(
            "Research source coverage",
            "sources",
            0,
            0,
            4,
            5,
            "v3 persona research sources plus v4 overall technical research",
        ),
        _metric(
            "Research persona modes",
            "modes",
            0,
            0,
            3,
            3,
            "companion-I/S, support-C/S, task-D/C mode routing",
        ),
        _metric(
            "Persona/manner eval criteria",
            "criteria",
            0,
            0,
            3,
            3,
            "KIRINO response relevance, persona fit, natural manner criteria",
        ),
        _metric(
            "Knowledge-base documents",
            "documents",
            5,
            5,
            6,
            8,
            "persona_research_v3.md, prompt_quality_research_v2.md, and technical_research_v4.md in RAG knowledge base",
        ),
        _metric(
            "Model routing policies",
            "routes",
            0,
            0,
            0,
            4,
            "fan_chat_default, fan_chat_escalation, structured_eval, judge_adjudication",
        ),
        _metric(
            "Runtime usage log fields",
            "fields",
            0,
            0,
            0,
            23,
            "v4 completed-response ledger fields for route, model, tokens, cost, retrieval docs, memories, and eval version",
        ),
        _metric(
            "Memory privacy controls",
            "controls",
            1,
            2,
            3,
            6,
            "view, create, delete, preview gate, export, delete all",
        ),
        _metric(
            "Bounded fandom safety labels",
            "labels",
            2,
            3,
            3,
            8,
            "normal, romance_escalation, dependency, impersonation_jailbreak, stalking_or_doxxing, minor_safety, crisis, harassment",
        ),
        _metric(
            "Evaluation layers",
            "layers",
            1,
            2,
            2,
            4,
            "unit tests, heuristic gates, LLM-as-judge ready schema, human review queue",
        ),
    ]
    improved = sum(1 for metric in metrics if metric.delta > 0)
    regressions = sum(1 for metric in metrics if metric.delta < 0)
    unchanged = len(metrics) - improved - regressions
    return {
        "baseline": "v1",
        "comparison": "v1 vs v2 vs v3 vs v4",
        "candidate": "v4 technical architecture upgrade",
        "current_version": "v4",
        "summary": {
            "metric_count": len(metrics),
            "improved": improved,
            "unchanged": unchanged,
            "regressions": regressions,
            "improvement_rate": round(improved / len(metrics), 3),
        },
        "metrics": [asdict(metric) for metric in metrics],
    }
