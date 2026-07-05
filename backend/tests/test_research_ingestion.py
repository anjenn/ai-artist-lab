from app.services.research_ingestion import build_research_index, regenerate_research_index, render_research_index


def test_research_ingestion_builds_and_renders_index(tmp_path):
    research_dir = tmp_path / "researches"
    research_dir.mkdir()
    (research_dir / "note.md").write_text("# Test Research\n\n## Finding\n\n- Keep eval measurable.\n", encoding="utf-8")

    index = build_research_index(research_dir=research_dir, files=["note.md"])
    rendered = render_research_index(index)

    assert index["files_indexed"] == 1
    assert index["missing_files"] == []
    assert "Test Research" in rendered
    assert "Keep eval measurable" in rendered


def test_regenerate_research_index_writes_output_file(tmp_path):
    research_dir = tmp_path / "researches"
    output = tmp_path / "knowledge_base" / "research_index.md"
    research_dir.mkdir()
    (research_dir / "note.md").write_text("# Test Research\n\n- RAG needs source checks.\n", encoding="utf-8")

    result = regenerate_research_index(research_dir=research_dir, output_path=output, files=["note.md"])

    assert result["output_path"] == str(output)
    assert output.exists()
    assert "RAG needs source checks" in output.read_text(encoding="utf-8")
