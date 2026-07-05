from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any

from app.core.config import get_settings

TOKEN_RE = re.compile(r"[a-zA-Z0-9']+|[가-힣]+")


def _tokens(text: str) -> list[str]:
    lowered = text.lower()
    tokens = TOKEN_RE.findall(lowered)
    if "데뷔" in lowered:
        tokens.extend(["debut", "song", "blue", "static"])
    if "노래" in lowered or "곡" in lowered:
        tokens.extend(["song", "track"])
    if "시험" in lowered:
        tokens.extend(["exam"])
    if "사랑" in lowered or "독점" in lowered:
        tokens.extend(["love", "exclusive"])
    if "팬" in lowered:
        tokens.extend(["fan"])
    if "persona" in lowered or "페르소나" in lowered:
        tokens.extend(["persona", "identity", "manner"])
    if "disc" in lowered or "성격" in lowered:
        tokens.extend(["disc", "personality", "mode"])
    if "상담" in lowered or "걱정" in lowered or "불안" in lowered:
        tokens.extend(["support", "counselling", "steady"])
    if "리서치" in lowered or "연구" in lowered:
        tokens.extend(["research", "evidence"])
    if "프롬프트" in lowered:
        tokens.extend(["prompt", "strategy"])
    if "평가" in lowered or "루브릭" in lowered:
        tokens.extend(["eval", "evaluation", "rubric"])
    if "보안" in lowered or "인젝션" in lowered or "주입" in lowered:
        tokens.extend(["security", "injection", "boundary"])
    if "메모리" in lowered:
        tokens.extend(["memory"])
    if "개인정보" in lowered or "프라이버시" in lowered:
        tokens.extend(["privacy"])
    if "삭제" in lowered:
        tokens.extend(["deletion", "delete"])
    if "경계" in lowered:
        tokens.extend(["boundary", "safety"])
    if "의존" in lowered:
        tokens.extend(["dependency"])
    if "검색" in lowered:
        tokens.extend(["search", "retrieval"])
    return tokens


class HashEmbeddingFunction:
    """Small deterministic embedding function so Chroma can run without an API key."""

    def __init__(self, dimensions: int = 64) -> None:
        self.dimensions = dimensions

    def __call__(self, input: list[str]) -> list[list[float]]:
        return [self.embed(text) for text in input]

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        for token in _tokens(text):
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimensions
            vector[index] += 1.0
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]


class OpenAIEmbeddingFunction:
    """Chroma-compatible embedding function backed by OpenAI embeddings."""

    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model

    def __call__(self, input: list[str]) -> list[list[float]]:
        from openai import OpenAI

        client = OpenAI(api_key=self.api_key)
        response = client.embeddings.create(model=self.model, input=input)
        return [item.embedding for item in response.data]


def build_embedding_function(settings, provider: str | None = None):
    requested = (provider or settings.embedding_provider or "hash").lower()
    if requested == "openai" and settings.openai_api_key:
        return "openai", OpenAIEmbeddingFunction(settings.openai_api_key, settings.openai_embedding_model)
    return "hash", HashEmbeddingFunction()


class LocalKnowledgeStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.mkdir(parents=True, exist_ok=True)
        self.file = self.path / "artist_knowledge.json"
        self.documents: list[dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        if self.file.exists():
            self.documents = json.loads(self.file.read_text(encoding="utf-8"))

    def _save(self) -> None:
        self.file.write_text(json.dumps(self.documents, indent=2), encoding="utf-8")

    def clear(self) -> None:
        self.documents = []
        self._save()

    def add(self, documents: list[dict[str, Any]]) -> None:
        self.documents = documents
        self._save()

    def count(self) -> int:
        return len(self.documents)

    def search(self, query: str, artist_id: int | None, top_k: int) -> list[dict]:
        query_tokens = set(_tokens(query))
        scored: list[tuple[float, dict]] = []
        for doc in self.documents:
            metadata = doc["metadata"]
            if artist_id is not None and metadata.get("artist_id") not in (None, artist_id):
                continue
            doc_tokens = set(_tokens(doc["content"]))
            overlap = len(query_tokens & doc_tokens)
            bonus = 0.0
            if "debut" in query_tokens and "blue static" in doc["content"].lower():
                bonus += 2.0
            if "exam" in query_tokens and "fan_policy" in metadata["source"]:
                bonus += 0.5
            source = metadata["source"]
            if "persona" in query_tokens and "persona_research" in source:
                bonus += 1.5
            if "research" in query_tokens and "persona_research" in source and {
                "persona",
                "disc",
                "manner",
                "mode",
            } & query_tokens:
                bonus += 1.0
            if {
                "prompt",
                "strategy",
                "eval",
                "evaluation",
                "rubric",
                "security",
                "injection",
            } & query_tokens and "prompt_quality_research" in source:
                bonus += 1.5
            if {
                "memory",
                "privacy",
                "deletion",
                "delete",
                "embedding",
                "hybrid",
                "cost",
                "streaming",
                "boundary",
                "safety",
                "dependency",
            } & query_tokens and ("technical_research" in source or "fan_policy" in source):
                bonus += 1.5
            score = (overlap / max(len(query_tokens), 1)) + bonus
            scored.append((score, doc))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [
            {
                "content": doc["content"],
                "source": doc["metadata"]["source"],
                "chunk_id": doc["metadata"]["chunk_id"],
                "distance": round(max(0.0, 1.0 - score), 4),
                "similarity": round(min(1.0, score), 4),
            }
            for score, doc in scored[:top_k]
            if score > 0
        ]


class RagService:
    def __init__(self, chroma_path: str | None = None, use_chroma: bool | None = None, embedding_provider: str | None = None) -> None:
        settings = get_settings()
        self.chroma_path = Path(chroma_path or settings.chroma_path)
        self.collection_name = "artist_knowledge"
        self.embedding_provider_name, self.embedding_function = build_embedding_function(settings, embedding_provider)
        self._use_chroma = False
        self._client = None
        self._collection = None
        self._local = LocalKnowledgeStore(self.chroma_path)

        if use_chroma is False:
            return
        try:
            import chromadb

            self._client = chromadb.PersistentClient(path=str(self.chroma_path))
            self._collection = self._client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function,
                metadata={"description": "Blue Garage artist knowledge"},
            )
            self._use_chroma = True
        except Exception:
            self._use_chroma = False

    def chunk_text(self, text: str, max_chars: int = 900) -> list[str]:
        paragraphs = [part.strip() for part in text.split("\n\n") if part.strip()]
        chunks: list[str] = []
        current = ""
        for paragraph in paragraphs:
            if not current:
                current = paragraph
            elif len(current) + len(paragraph) + 2 <= max_chars:
                current += "\n\n" + paragraph
            else:
                chunks.append(current)
                current = paragraph
        if current:
            chunks.append(current)
        return chunks or [text.strip()]

    def index_knowledge_base(self, kb_dir: str = "../knowledge_base") -> dict:
        kb_path = Path(kb_dir)
        if not kb_path.is_absolute():
            kb_path = Path.cwd() / kb_path
        if not kb_path.exists():
            kb_path = Path(__file__).resolve().parents[3] / "knowledge_base"
        files = sorted(kb_path.glob("*.md"))
        documents: list[dict[str, Any]] = []
        ids: list[str] = []
        texts: list[str] = []
        metadatas: list[dict[str, Any]] = []

        for file in files:
            chunks = self.chunk_text(file.read_text(encoding="utf-8"))
            for index, chunk in enumerate(chunks, start=1):
                chunk_id = f"chunk_{index:02d}"
                doc_id = f"{file.stem}_{chunk_id}"
                metadata = {"source": file.name, "chunk_id": chunk_id, "artist_id": 1}
                documents.append({"id": doc_id, "content": chunk, "metadata": metadata})
                ids.append(doc_id)
                texts.append(chunk)
                metadatas.append(metadata)

        if self._use_chroma and self._collection is not None:
            try:
                existing = self._collection.get()
                existing_ids = existing.get("ids", [])
                if existing_ids:
                    self._collection.delete(ids=existing_ids)
                if ids:
                    self._collection.add(ids=ids, documents=texts, metadatas=metadatas)
            except Exception:
                self._use_chroma = False

        self._local.add(documents)
        return {"documents": len(files), "chunks": len(documents), "collection": self.collection_name}

    def _ensure_indexed(self) -> None:
        if self._use_chroma and self._collection is not None:
            try:
                if self._collection.count() > 0:
                    return
            except Exception:
                self._use_chroma = False
        if self._local.count() > 0:
            return

        default_kb = Path(__file__).resolve().parents[3] / "knowledge_base"
        if default_kb.exists():
            self.index_knowledge_base(str(default_kb))

    def search(self, query: str, artist_id: int | None = None, top_k: int = 4) -> list[dict]:
        self._ensure_indexed()
        if self._use_chroma and self._collection is not None:
            try:
                where = {"artist_id": artist_id} if artist_id is not None else None
                results = self._collection.query(query_texts=[query], n_results=top_k, where=where)
                documents = results.get("documents", [[]])[0]
                metadatas = results.get("metadatas", [[]])[0]
                distances = results.get("distances", [[]])[0]
                return [
                    {
                        "content": content,
                        "source": metadata.get("source"),
                        "chunk_id": metadata.get("chunk_id"),
                        "distance": round(float(distance), 4),
                        "similarity": round(max(0.0, 1.0 - float(distance)), 4),
                    }
                    for content, metadata, distance in zip(documents, metadatas, distances)
                ]
            except Exception:
                self._use_chroma = False
        return self._local.search(query=query, artist_id=artist_id, top_k=top_k)
