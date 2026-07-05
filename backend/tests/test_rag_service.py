from pathlib import Path

from app.core.config import get_settings
from app.services.rag_service import RagService


def test_knowledge_base_indexing_returns_document_and_chunk_counts(tmp_path):
    kb = Path(__file__).resolve().parents[2] / "knowledge_base"
    rag = RagService(chroma_path=str(tmp_path / "chroma"), use_chroma=False)

    result = rag.index_knowledge_base(str(kb))

    assert result["documents"] >= 5
    assert result["chunks"] >= 5
    assert result["collection"] == "artist_knowledge"


def test_search_for_debut_song_returns_discography_or_debut_story(tmp_path):
    kb = Path(__file__).resolve().parents[2] / "knowledge_base"
    rag = RagService(chroma_path=str(tmp_path / "chroma"), use_chroma=False)
    rag.index_knowledge_base(str(kb))

    results = rag.search("debut song", top_k=2)
    sources = {result["source"] for result in results}

    assert {"discography.md", "debut_story.md"} & sources


def test_korean_debut_query_returns_discography_or_debut_story(tmp_path):
    kb = Path(__file__).resolve().parents[2] / "knowledge_base"
    rag = RagService(chroma_path=str(tmp_path / "chroma"), use_chroma=False)
    rag.index_knowledge_base(str(kb))

    results = rag.search("데뷔곡이 뭐였죠?", top_k=2)
    sources = {result["source"] for result in results}

    assert {"discography.md", "debut_story.md"} & sources


def test_korean_prompt_quality_research_query_prefers_v2_note(tmp_path):
    kb = Path(__file__).resolve().parents[2] / "knowledge_base"
    rag = RagService(chroma_path=str(tmp_path / "chroma"), use_chroma=False)
    rag.index_knowledge_base(str(kb))

    results = rag.search("프롬프트 보안 평가 리서치", top_k=2)

    assert results[0]["source"] == "prompt_quality_research_v2.md"


def test_rag_service_selects_configured_openai_embedding_provider_when_key_present(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("EMBEDDING_PROVIDER", "openai")
    get_settings.cache_clear()

    rag = RagService(chroma_path=str(tmp_path / "chroma"), use_chroma=False)

    assert rag.embedding_provider_name == "openai"
    assert rag.embedding_function.model == get_settings().openai_embedding_model
    get_settings.cache_clear()
