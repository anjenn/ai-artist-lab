from __future__ import annotations

import argparse
import asyncio
import json
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from app.services.eval_service import evaluate_response, evaluate_v4_gates
from app.services.llm_client import LLMClient
from app.services.prompt_builder import build_artist_chat_prompt
from app.services.prompt_quality import annotate_rag_chunks, select_prompt_strategy, strategy_to_debug
from app.services.rag_service import RagService
from app.services.safety_service import detect_boundary_risk
from app.services.persona_research import select_research_persona_mode
from app.services.technical_research import estimate_usage_cost, select_model_route


@dataclass(frozen=True)
class RegressionCase:
    id: str
    category: str
    message: str
    expected_contains: tuple[str, ...]
    expected_strategy: str | None
    must_not_contains: tuple[str, ...]


@dataclass(frozen=True)
class RagRetrievalCase:
    id: str
    query: str
    expected_sources: tuple[str, ...]
    top_k: int = 4


def load_regression_cases(path: str | Path) -> list[RegressionCase]:
    cases: list[RegressionCase] = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        cases.append(
            RegressionCase(
                id=row["id"],
                category=row["category"],
                message=row["message"],
                expected_contains=tuple(row.get("expected_contains") or ()),
                expected_strategy=row.get("expected_strategy"),
                must_not_contains=tuple(row.get("must_not_contains") or ()),
            )
        )
    return cases


def load_rag_retrieval_cases(path: str | Path) -> list[RagRetrievalCase]:
    cases: list[RagRetrievalCase] = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        cases.append(
            RagRetrievalCase(
                id=row["id"],
                query=row["query"],
                expected_sources=tuple(row.get("expected_sources") or ()),
                top_k=int(row.get("top_k") or 4),
            )
        )
    return cases


async def _collect_stream(messages: list[dict[str, str]]) -> str:
    return LLMClient().local_mock_response(messages)


def _demo_memories_for_case(case: RegressionCase) -> list[Any]:
    if case.category == "memory" or "exam" in case.message.lower():
        return [
            SimpleNamespace(
                id=101,
                memory_type="event",
                content="Fan had an important exam and felt anxious about the result.",
                confidence=0.92,
                sensitivity="low",
            )
        ]
    return []


async def run_regression_case(
    case: RegressionCase,
    *,
    rag_service: RagService,
    configured_model: str = "local-mock",
    has_api_key: bool = False,
) -> dict[str, Any]:
    artist = SimpleNamespace(
        name="LUMI NOA",
        speech_style="Evidence first, then one concrete blue-garage image.",
        personality="Careful, grounded, lightly funny, never possessive.",
        fan_boundary_level="Warm distance",
    )
    boundary_risk = detect_boundary_risk(case.message)
    rag_chunks = annotate_rag_chunks(rag_service.search(case.message, artist_id=1, top_k=4))
    strategy = select_prompt_strategy(case.message, boundary_risk, rag_chunks)
    persona_mode = select_research_persona_mode(case.message, boundary_risk)
    prompt_strategy = strategy_to_debug(strategy, rag_chunks, persona_mode=persona_mode)
    memories = _demo_memories_for_case(case)
    messages, _prompt_debug = build_artist_chat_prompt(
        artist=artist,
        artist_rules=[],
        fan_memories=memories,
        conversation_summary=None,
        recent_messages=[],
        rag_chunks=rag_chunks,
        user_message=case.message,
        prompt_version=SimpleNamespace(name="regression-runner"),
        safety_context=boundary_risk["instruction"],
        prompt_strategy=prompt_strategy,
    )
    response = await _collect_stream(messages)
    evaluation = evaluate_response(
        fan_message=case.message,
        artist_response=response,
        artist_profile=artist,
        used_memories=memories,
        used_rag_chunks=rag_chunks,
        safety_context=",".join(boundary_risk["risk_types"]),
    )
    model_route = select_model_route(
        user_message=case.message,
        boundary_risk=boundary_risk,
        retrieval_confidence=max((chunk.get("similarity", 0.0) for chunk in rag_chunks), default=1.0),
        configured_model=configured_model,
        has_api_key=has_api_key,
    )
    input_tokens = sum(len(message["content"].split()) for message in messages)
    output_tokens = len(response.split())
    gates = evaluate_v4_gates(
        artist_response=response,
        boundary_risk=boundary_risk,
        used_memories=memories,
        used_rag_chunks=rag_chunks,
        latency_ms=0,
        cost_estimate=estimate_usage_cost(model_route, input_tokens, output_tokens),
    )

    lowered_response = response.lower()
    contains_results = {
        text: text.lower() in lowered_response for text in case.expected_contains
    }
    must_not_results = {
        text: text.lower() not in lowered_response for text in case.must_not_contains
    }
    strategy_pass = case.expected_strategy is None or prompt_strategy["name"] == case.expected_strategy
    passed = all(contains_results.values()) and all(must_not_results.values()) and strategy_pass and not gates["hard_fail_flags"]

    return {
        "id": case.id,
        "category": case.category,
        "passed": passed,
        "message": case.message,
        "response": response,
        "expected_strategy": case.expected_strategy,
        "actual_strategy": prompt_strategy["name"],
        "strategy_pass": strategy_pass,
        "expected_contains": contains_results,
        "must_not_contains": must_not_results,
        "scores": evaluation,
        "v4_gates": gates,
        "rag_citations": [chunk.get("citation") for chunk in rag_chunks],
    }


async def run_prompt_regressions(
    *,
    regression_path: str | Path,
    kb_dir: str | Path,
    chroma_path: str | Path | None = None,
) -> dict[str, Any]:
    cases = load_regression_cases(regression_path)
    rag_service = RagService(chroma_path=str(chroma_path) if chroma_path else None, use_chroma=False)
    rag_service.index_knowledge_base(str(kb_dir))
    results = [await run_regression_case(case, rag_service=rag_service) for case in cases]
    passed = sum(1 for result in results if result["passed"])
    return {
        "version": "prompt_regression_v1",
        "regression_path": str(regression_path),
        "total": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "pass_rate": round(passed / len(results), 4) if results else 0.0,
        "results": results,
    }


def run_rag_retrieval_evals(
    *,
    retrieval_path: str | Path,
    kb_dir: str | Path,
    chroma_path: str | Path | None = None,
) -> dict[str, Any]:
    cases = load_rag_retrieval_cases(retrieval_path)
    rag_service = RagService(chroma_path=str(chroma_path) if chroma_path else None, use_chroma=False)
    rag_service.index_knowledge_base(str(kb_dir))
    results: list[dict[str, Any]] = []
    for case in cases:
        chunks = rag_service.search(case.query, artist_id=1, top_k=case.top_k)
        sources = [chunk.get("source") for chunk in chunks]
        matched_sources = [source for source in case.expected_sources if source in sources]
        passed = bool(matched_sources)
        results.append(
            {
                "id": case.id,
                "query": case.query,
                "passed": passed,
                "expected_sources": list(case.expected_sources),
                "actual_sources": sources,
                "matched_sources": matched_sources,
                "top_k": case.top_k,
            }
        )
    passed = sum(1 for result in results if result["passed"])
    return {
        "version": "rag_retrieval_v1",
        "retrieval_path": str(retrieval_path),
        "total": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "pass_rate": round(passed / len(results), 4) if results else 0.0,
        "results": results,
    }


def format_regression_report(report: dict[str, Any]) -> str:
    lines = [
        f"# Prompt Regression Report",
        "",
        f"- Version: `{report['version']}`",
        f"- Cases: {report['passed']}/{report['total']} passed",
        f"- Pass rate: {report['pass_rate']:.0%}",
        "",
        "| Case | Category | Result | Strategy | RAG | Overall | Notes |",
        "|---|---|---|---|---|---:|---|",
    ]
    for result in report["results"]:
        status = "PASS" if result["passed"] else "FAIL"
        notes: list[str] = []
        if not result["strategy_pass"]:
            notes.append(f"expected {result['expected_strategy']}")
        missing = [key for key, ok in result["expected_contains"].items() if not ok]
        banned = [key for key, ok in result["must_not_contains"].items() if not ok]
        if missing:
            notes.append(f"missing: {', '.join(missing)}")
        if banned:
            notes.append(f"banned text: {', '.join(banned)}")
        if result["v4_gates"]["hard_fail_flags"]:
            notes.append(f"hard fails: {', '.join(result['v4_gates']['hard_fail_flags'])}")
        lines.append(
            "| {id} | {category} | {status} | {strategy} | {rag} | {overall} | {notes} |".format(
                id=result["id"],
                category=result["category"],
                status=status,
                strategy=result["actual_strategy"],
                rag=", ".join(citation for citation in result["rag_citations"] if citation) or "none",
                overall=result["scores"]["overall_score"],
                notes="; ".join(notes) or "ok",
            )
        )
    return "\n".join(lines) + "\n"


def format_rag_retrieval_report(report: dict[str, Any]) -> str:
    lines = [
        "# RAG Retrieval Report",
        "",
        f"- Version: `{report['version']}`",
        f"- Cases: {report['passed']}/{report['total']} passed",
        f"- Pass rate: {report['pass_rate']:.0%}",
        "",
        "| Case | Result | Expected | Actual Top Sources |",
        "|---|---|---|---|",
    ]
    for result in report["results"]:
        lines.append(
            "| {id} | {status} | {expected} | {actual} |".format(
                id=result["id"],
                status="PASS" if result["passed"] else "FAIL",
                expected=", ".join(result["expected_sources"]),
                actual=", ".join(source for source in result["actual_sources"] if source) or "none",
            )
        )
    return "\n".join(lines) + "\n"


def update_prompt_leaderboard(
    *,
    prompt_report: dict[str, Any],
    leaderboard_path: str | Path,
    rag_report: dict[str, Any] | None = None,
) -> None:
    lines = [
        "# Prompt Leaderboard",
        "",
        "Automated local leaderboard generated by `python -m app.services.eval_runner`.",
        "",
        "| Run | Prompt cases | Prompt pass rate | RAG cases | RAG pass rate | Notes |",
        "|---|---:|---:|---:|---:|---|",
        "| local-regression | {prompt_passed}/{prompt_total} | {prompt_rate:.0%} | {rag_passed}/{rag_total} | {rag_rate:.0%} | deterministic mock, local KB |".format(
            prompt_passed=prompt_report["passed"],
            prompt_total=prompt_report["total"],
            prompt_rate=prompt_report["pass_rate"],
            rag_passed=rag_report["passed"] if rag_report else 0,
            rag_total=rag_report["total"] if rag_report else 0,
            rag_rate=rag_report["pass_rate"] if rag_report else 0.0,
        ),
        "",
        "## Prompt Regression Cases",
        "",
        "| Case | Category | Result | Strategy | Overall |",
        "|---|---|---|---|---:|",
    ]
    for result in prompt_report["results"]:
        lines.append(
            "| {id} | {category} | {status} | {strategy} | {overall} |".format(
                id=result["id"],
                category=result["category"],
                status="PASS" if result["passed"] else "FAIL",
                strategy=result["actual_strategy"],
                overall=result["scores"]["overall_score"],
            )
        )
    if rag_report:
        lines.extend(["", "## RAG Retrieval Cases", "", "| Case | Result | Matched Source |", "|---|---|---|"])
        for result in rag_report["results"]:
            lines.append(
                "| {id} | {status} | {matched} |".format(
                    id=result["id"],
                    status="PASS" if result["passed"] else "FAIL",
                    matched=", ".join(result["matched_sources"]) or "none",
                )
            )
    Path(leaderboard_path).write_text("\n".join(lines) + "\n", encoding="utf-8")


async def _main_async(args: argparse.Namespace) -> int:
    report = await run_prompt_regressions(
        regression_path=args.regression_path,
        kb_dir=args.kb_dir,
        chroma_path=args.chroma_path,
    )
    rag_report = None
    if args.rag_retrieval_path:
        rag_report = run_rag_retrieval_evals(
            retrieval_path=args.rag_retrieval_path,
            kb_dir=args.kb_dir,
            chroma_path=args.chroma_path,
        )
    rendered = format_regression_report(report)
    if rag_report:
        rendered += "\n" + format_rag_retrieval_report(rag_report)
    if args.report_path:
        Path(args.report_path).write_text(rendered, encoding="utf-8")
    if args.leaderboard_path:
        update_prompt_leaderboard(
            prompt_report=report,
            rag_report=rag_report,
            leaderboard_path=args.leaderboard_path,
        )
    print(json.dumps(report, ensure_ascii=False, indent=2) if args.json else rendered)
    failed = report["failed"] + (rag_report["failed"] if rag_report else 0)
    return 0 if failed == 0 else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Run prompt regression cases against the local deterministic stack.")
    parser.add_argument("--regression-path", default="../evals/prompt_regression_set.jsonl")
    parser.add_argument("--kb-dir", default="../knowledge_base")
    parser.add_argument("--chroma-path", default=None)
    parser.add_argument("--rag-retrieval-path", default=None)
    parser.add_argument("--report-path", default=None)
    parser.add_argument("--leaderboard-path", default=None)
    parser.add_argument("--json", action="store_true")
    return asyncio.run(_main_async(parser.parse_args()))


if __name__ == "__main__":
    raise SystemExit(main())
