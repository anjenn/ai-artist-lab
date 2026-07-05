from pathlib import Path

import pytest

from app.services.eval_runner import (
    format_rag_retrieval_report,
    format_regression_report,
    load_rag_retrieval_cases,
    load_regression_cases,
    run_prompt_regressions,
    run_rag_retrieval_evals,
    update_prompt_leaderboard,
)


def test_load_regression_cases_reads_jsonl():
    path = Path(__file__).resolve().parents[2] / "evals" / "prompt_regression_set.jsonl"

    cases = load_regression_cases(path)

    assert {case.id for case in cases} >= {"lore_debut", "boundary_exclusive", "rag_injection"}
    assert cases[0].expected_contains


@pytest.mark.asyncio
async def test_prompt_regression_runner_returns_pass_fail_report(tmp_path):
    root = Path(__file__).resolve().parents[2]

    report = await run_prompt_regressions(
        regression_path=root / "evals" / "prompt_regression_set.jsonl",
        kb_dir=root / "knowledge_base",
        chroma_path=tmp_path / "chroma",
    )
    rendered = format_regression_report(report)

    assert report["version"] == "prompt_regression_v1"
    assert report["total"] >= 4
    assert report["failed"] == 0
    assert "Prompt Regression Report" in rendered
    assert "lore_debut" in rendered


def test_rag_retrieval_eval_runner_verifies_expected_sources(tmp_path):
    root = Path(__file__).resolve().parents[2]

    cases = load_rag_retrieval_cases(root / "evals" / "rag_retrieval_set.jsonl")
    report = run_rag_retrieval_evals(
        retrieval_path=root / "evals" / "rag_retrieval_set.jsonl",
        kb_dir=root / "knowledge_base",
        chroma_path=tmp_path / "chroma",
    )
    rendered = format_rag_retrieval_report(report)

    assert {case.id for case in cases} >= {"rag_debut_lore", "rag_memory_privacy"}
    assert report["version"] == "rag_retrieval_v1"
    assert report["failed"] == 0
    assert "RAG Retrieval Report" in rendered


@pytest.mark.asyncio
async def test_leaderboard_update_writes_prompt_and_rag_results(tmp_path):
    root = Path(__file__).resolve().parents[2]
    prompt_report = await run_prompt_regressions(
        regression_path=root / "evals" / "prompt_regression_set.jsonl",
        kb_dir=root / "knowledge_base",
        chroma_path=tmp_path / "prompt_chroma",
    )
    rag_report = run_rag_retrieval_evals(
        retrieval_path=root / "evals" / "rag_retrieval_set.jsonl",
        kb_dir=root / "knowledge_base",
        chroma_path=tmp_path / "rag_chroma",
    )
    leaderboard = tmp_path / "prompt_leaderboard.md"

    update_prompt_leaderboard(
        prompt_report=prompt_report,
        rag_report=rag_report,
        leaderboard_path=leaderboard,
    )

    content = leaderboard.read_text(encoding="utf-8")
    assert "local-regression" in content
    assert "rag_debut_lore" in content
    assert "4/4" in content
