"""Knowledge-base indexing and retrieval endpoints."""

from pathlib import Path

from fastapi import APIRouter, Query

from app.schemas.kb import KnowledgeDocumentCreate
from app.services.rag_service import RagService

router = APIRouter(prefix="/kb", tags=["knowledge-base"])


@router.post("/reindex")
def reindex_knowledge_base() -> dict:
    return RagService().index_knowledge_base("../knowledge_base")


@router.post("/documents")
def create_knowledge_document(payload: KnowledgeDocumentCreate) -> dict:
    kb_dir = Path(__file__).resolve().parents[3] / "knowledge_base"
    kb_dir.mkdir(parents=True, exist_ok=True)
    path = kb_dir / payload.filename
    path.write_text(payload.content, encoding="utf-8")
    index_result = RagService().index_knowledge_base(str(kb_dir))
    return {"filename": payload.filename, "bytes": len(payload.content.encode("utf-8")), "index": index_result}


@router.get("/search")
def search_knowledge_base(q: str = Query(min_length=1), artist_id: int | None = 1, top_k: int = 4) -> dict:
    results = RagService().search(q, artist_id=artist_id, top_k=top_k)
    return {"query": q, "results": results}
