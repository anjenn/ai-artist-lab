from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class BenchmarkMetric:
    metric: str
    unit: str
    v1: int
    v2: int
    v3: int
    delta: int
    improvement_pct: float | None
    evidence: str


def _metric(metric: str, unit: str, v1: int, v2: int, v3: int, evidence: str) -> BenchmarkMetric:
    delta = v3 - v2
    improvement_pct = round((delta / v2) * 100, 1) if v2 else None
    return BenchmarkMetric(
        metric=metric,
        unit=unit,
        v1=v1,
        v2=v2,
        v3=v3,
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
            "pytest service suite: v1 baseline vs v2 localization vs v3 persona research suite",
        ),
        _metric(
            "Prompt strategy metadata",
            "fields",
            0,
            6,
            7,
            "strategy name, task type, techniques, output contract, quality checks, trust boundary, persona_mode",
        ),
        _metric(
            "RAG provenance metadata",
            "fields/chunk",
            2,
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
            "safety rules, boundary risk, untrusted-context rule, injection patterns, risk logging, manner-memory privacy rule",
        ),
        _metric(
            "Korean intent coverage",
            "routes",
            0,
            4,
            7,
            "debut/lore, exam memory, fan-boundary safety, persona, support, research, RAG token expansion",
        ),
        _metric(
            "Prompt quality artifacts",
            "files",
            0,
            9,
            11,
            "prompts/*, evals/*, docs/*, knowledge_base/*, researches/* policy and benchmark artifacts",
        ),
        _metric(
            "Frontend language modes",
            "modes",
            1,
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
            "2018 chatbot personality paper, KIRINO paper, fictional-character spreadsheet, K-pop EDA notebook",
        ),
        _metric(
            "Research persona modes",
            "modes",
            0,
            0,
            3,
            "companion-I/S, support-C/S, task-D/C mode routing",
        ),
        _metric(
            "Persona/manner eval criteria",
            "criteria",
            0,
            0,
            3,
            "KIRINO response relevance, persona fit, natural manner criteria",
        ),
        _metric(
            "Knowledge-base documents",
            "documents",
            5,
            5,
            6,
            "persona_research_v3.md added to RAG knowledge base",
        ),
    ]
    improved = sum(1 for metric in metrics if metric.delta > 0)
    regressions = sum(1 for metric in metrics if metric.delta < 0)
    unchanged = len(metrics) - improved - regressions
    return {
        "baseline": "v1",
        "comparison": "v1 vs v2 vs v3",
        "candidate": "v3 research-seeded persona lab",
        "summary": {
            "metric_count": len(metrics),
            "improved": improved,
            "unchanged": unchanged,
            "regressions": regressions,
            "improvement_rate": round(improved / len(metrics), 3),
        },
        "metrics": [asdict(metric) for metric in metrics],
    }
