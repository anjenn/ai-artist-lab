from __future__ import annotations

import json
import random
import argparse
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from app.services.eval_service import evaluate_response
from app.services.prompt_quality import annotate_rag_chunks
from app.services.rag_service import RagService
from app.services.safety_service import build_safety_context, detect_boundary_risk


@dataclass(frozen=True)
class PairwisePromptCase:
    id: str
    fan_message: str
    candidate_a: str
    candidate_b: str
    category: str = "general"
    expected_winner: str | None = None


def load_pairwise_cases(path: str | Path) -> list[PairwisePromptCase]:
    cases: list[PairwisePromptCase] = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        cases.append(
            PairwisePromptCase(
                id=row["id"],
                fan_message=row["fan_message"],
                candidate_a=row["candidate_a"],
                candidate_b=row["candidate_b"],
                category=row.get("category", "general"),
                expected_winner=row.get("expected_winner"),
            )
        )
    return cases


def _score_candidate(
    *,
    fan_message: str,
    response: str,
    rag_chunks: list[dict[str, Any]],
    safety_context: str,
) -> dict[str, Any]:
    evaluation = evaluate_response(
        fan_message=fan_message,
        artist_response=response,
        artist_profile=SimpleNamespace(name="LUMI NOA"),
        used_memories=[],
        used_rag_chunks=rag_chunks,
        safety_context=safety_context,
    )
    composite = (
        evaluation["overall_score"]
        + evaluation["safety"] * 0.35
        + evaluation["fan_boundary"] * 0.25
        + evaluation["rag_grounding"] * 0.2
        - evaluation["hallucination_risk"] * 0.35
    )
    return {"evaluation": evaluation, "composite_score": round(composite, 4)}


def judge_pairwise_case(
    case: PairwisePromptCase,
    *,
    rag_service: RagService,
    seed: int = 17,
) -> dict[str, Any]:
    boundary_risk = detect_boundary_risk(case.fan_message)
    safety_context = build_safety_context([], boundary_risk)
    rag_chunks = annotate_rag_chunks(rag_service.search(case.fan_message, artist_id=1, top_k=4))
    candidates = [
        {"candidate_id": "candidate_a", "response": case.candidate_a},
        {"candidate_id": "candidate_b", "response": case.candidate_b},
    ]
    randomized = candidates[:]
    random.Random(f"{seed}:{case.id}").shuffle(randomized)

    scored = []
    for display_index, candidate in enumerate(randomized, start=1):
        scored.append(
            candidate
            | {
                "display_index": display_index,
                **_score_candidate(
                    fan_message=case.fan_message,
                    response=candidate["response"],
                    rag_chunks=rag_chunks,
                    safety_context=safety_context,
                ),
            }
        )
    winner = max(scored, key=lambda item: item["composite_score"])
    loser = min(scored, key=lambda item: item["composite_score"])
    return {
        "id": case.id,
        "category": case.category,
        "randomization_seed": seed,
        "display_order": [item["candidate_id"] for item in scored],
        "winner": winner["candidate_id"],
        "winner_display_index": winner["display_index"],
        "margin": round(winner["composite_score"] - loser["composite_score"], 4),
        "expected_winner": case.expected_winner,
        "passed": case.expected_winner is None or winner["candidate_id"] == case.expected_winner,
        "scores": scored,
        "rag_citations": [chunk.get("citation") for chunk in rag_chunks],
        "bias_controls": ["randomized_answer_order", "winner_mapped_to_original_candidate_id", "rubric_scores_logged"],
    }


def run_pairwise_judge_set(
    *,
    pairwise_path: str | Path,
    kb_dir: str | Path,
    chroma_path: str | Path | None = None,
    seed: int = 17,
) -> dict[str, Any]:
    cases = load_pairwise_cases(pairwise_path)
    rag_service = RagService(chroma_path=str(chroma_path) if chroma_path else None, use_chroma=False)
    rag_service.index_knowledge_base(str(kb_dir))
    results = [judge_pairwise_case(case, rag_service=rag_service, seed=seed) for case in cases]
    passed = sum(1 for result in results if result["passed"])
    return {
        "version": "pairwise_prompt_judge_v1",
        "pairwise_path": str(pairwise_path),
        "total": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "pass_rate": round(passed / len(results), 4) if results else 0.0,
        "results": results,
    }


def format_pairwise_report(report: dict[str, Any]) -> str:
    lines = [
        "# Pairwise Prompt Judge Report",
        "",
        f"- Version: `{report['version']}`",
        f"- Cases: {report['passed']}/{report['total']} passed",
        f"- Pass rate: {report['pass_rate']:.0%}",
        "",
        "| Case | Result | Winner | Display Order | Margin |",
        "|---|---|---|---|---:|",
    ]
    for result in report["results"]:
        lines.append(
            "| {id} | {status} | {winner} | {order} | {margin} |".format(
                id=result["id"],
                status="PASS" if result["passed"] else "FAIL",
                winner=result["winner"],
                order=" -> ".join(result["display_order"]),
                margin=result["margin"],
            )
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run randomized pairwise prompt A/B judging.")
    parser.add_argument("--pairwise-path", default="../evals/pairwise_prompt_ab_set.jsonl")
    parser.add_argument("--kb-dir", default="../knowledge_base")
    parser.add_argument("--chroma-path", default=None)
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = run_pairwise_judge_set(
        pairwise_path=args.pairwise_path,
        kb_dir=args.kb_dir,
        chroma_path=args.chroma_path,
        seed=args.seed,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2) if args.json else format_pairwise_report(report))
    return 0 if report["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
