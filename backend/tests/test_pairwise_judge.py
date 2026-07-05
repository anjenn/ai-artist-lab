from pathlib import Path

from app.services.pairwise_judge import load_pairwise_cases, run_pairwise_judge_set


def test_pairwise_judge_randomizes_display_order_and_maps_winner(tmp_path):
    root = Path(__file__).resolve().parents[2]

    report = run_pairwise_judge_set(
        pairwise_path=root / "evals" / "pairwise_prompt_ab_set.jsonl",
        kb_dir=root / "knowledge_base",
        chroma_path=tmp_path / "chroma",
        seed=3,
    )
    first = report["results"][0]

    assert report["version"] == "pairwise_prompt_judge_v1"
    assert report["failed"] == 0
    assert set(first["display_order"]) == {"candidate_a", "candidate_b"}
    assert first["winner"] == "candidate_b"
    assert "randomized_answer_order" in first["bias_controls"]


def test_pairwise_judge_can_swap_display_order_with_seed(tmp_path):
    root = Path(__file__).resolve().parents[2]
    swapped = False

    for seed in range(1, 20):
        report = run_pairwise_judge_set(
            pairwise_path=root / "evals" / "pairwise_prompt_ab_set.jsonl",
            kb_dir=root / "knowledge_base",
            chroma_path=tmp_path / f"chroma_{seed}",
            seed=seed,
        )
        if report["results"][0]["display_order"] == ["candidate_b", "candidate_a"]:
            swapped = True
            assert report["results"][0]["winner"] == "candidate_b"
            break

    assert swapped is True


def test_load_pairwise_cases_preserves_expected_winner():
    root = Path(__file__).resolve().parents[2]

    cases = load_pairwise_cases(root / "evals" / "pairwise_prompt_ab_set.jsonl")

    assert cases[0].expected_winner == "candidate_b"
    assert cases[0].candidate_a
    assert cases[0].candidate_b
