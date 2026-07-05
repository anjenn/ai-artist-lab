from pathlib import Path

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
