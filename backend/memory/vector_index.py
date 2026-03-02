"""Vector index backends for long-term memory search."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional


@dataclass
class VectorSearchResult:
    """Search hit from vector index."""

    memory_id: str
    score: float


def _cosine_similarity(a: List[float], b: List[float]) -> float:
    if not a or not b:
        return 0.0
    n = min(len(a), len(b))
    dot = sum(a[i] * b[i] for i in range(n))
    norm_a = math.sqrt(sum(v * v for v in a[:n]))
    norm_b = math.sqrt(sum(v * v for v in b[:n]))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class BaseVectorIndex:
    """Vector index interface."""

    def upsert(self, memory_id: str, user_id: str, vector: List[float], metadata: Optional[Dict[str, Any]] = None) -> None:
        raise NotImplementedError

    def delete(self, memory_id: str) -> None:
        raise NotImplementedError

    def search(self, user_id: str, query_vector: List[float], top_k: int) -> List[VectorSearchResult]:
        raise NotImplementedError


class LocalFileVectorIndex(BaseVectorIndex):
    """Simple persistent local vector index fallback."""

    def __init__(self, persist_path: str):
        self.persist_path = Path(persist_path)
        self.persist_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        self._rows: Dict[str, Dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        if not self.persist_path.exists():
            return
        try:
            self._rows = json.loads(self.persist_path.read_text(encoding="utf-8"))
        except Exception:
            self._rows = {}

    def _save(self) -> None:
        self.persist_path.write_text(json.dumps(self._rows), encoding="utf-8")

    def upsert(self, memory_id: str, user_id: str, vector: List[float], metadata: Optional[Dict[str, Any]] = None) -> None:
        metadata = metadata or {}
        with self._lock:
            self._rows[memory_id] = {
                "user_id": user_id,
                "vector": vector,
                "metadata": metadata,
            }
            self._save()

    def delete(self, memory_id: str) -> None:
        with self._lock:
            if memory_id in self._rows:
                del self._rows[memory_id]
                self._save()

    def search(self, user_id: str, query_vector: List[float], top_k: int) -> List[VectorSearchResult]:
        candidates = []
        for memory_id, row in self._rows.items():
            if row.get("user_id") != user_id:
                continue
            score = _cosine_similarity(query_vector, row.get("vector", []))
            candidates.append(VectorSearchResult(memory_id=memory_id, score=score))
        candidates.sort(key=lambda r: r.score, reverse=True)
        return candidates[:top_k]


class ChromaVectorIndex(BaseVectorIndex):
    """Chroma-backed vector index."""

    def __init__(self, persist_directory: str, collection_name: str):
        import chromadb

        self._client = chromadb.PersistentClient(path=persist_directory)
        self._collection = self._client.get_or_create_collection(name=collection_name)

    def upsert(self, memory_id: str, user_id: str, vector: List[float], metadata: Optional[Dict[str, Any]] = None) -> None:
        payload = {"user_id": user_id}
        if metadata:
            payload.update(metadata)
        self._collection.upsert(
            ids=[memory_id],
            embeddings=[vector],
            metadatas=[payload],
        )

    def delete(self, memory_id: str) -> None:
        self._collection.delete(ids=[memory_id])

    def search(self, user_id: str, query_vector: List[float], top_k: int) -> List[VectorSearchResult]:
        result = self._collection.query(
            query_embeddings=[query_vector],
            n_results=max(1, top_k),
            where={"user_id": user_id},
            include=["distances"],
        )
        ids = result.get("ids", [[]])[0]
        distances = result.get("distances", [[]])[0]
        hits = []
        for memory_id, distance in zip(ids, distances):
            # Chroma returns distance; convert to a higher-is-better score.
            score = 1.0 - float(distance)
            hits.append(VectorSearchResult(memory_id=memory_id, score=score))
        return hits


def build_vector_index(backend: str, persist_dir: str, collection_name: str) -> BaseVectorIndex:
    if backend.lower() == "chroma":
        try:
            return ChromaVectorIndex(persist_directory=persist_dir, collection_name=collection_name)
        except Exception:
            pass
    return LocalFileVectorIndex(persist_path=str(Path(persist_dir) / "vectors.json"))

