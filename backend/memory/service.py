"""Orchestrates long-term memory CRUD, vector indexing, and semantic search."""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..config import AppConfig, ModelConfig
from .embeddings import EmbeddingProvider
from .repository import MemoryRepository
from .vector_index import VectorSearchResult, build_vector_index


@dataclass
class MemoryItem:
    """Memory entity returned to API and graph."""

    id: str
    user_id: str
    text: str
    tags: List[str]
    created_at: float
    updated_at: float
    metadata: Dict[str, Any]


@dataclass
class MemorySearchResult:
    """Search response tuple."""

    memory: MemoryItem
    score: float


class MemoryService:
    """Long-term memory service with CRUD + semantic search."""

    def __init__(
        self,
        repository: MemoryRepository,
        embedding_provider: EmbeddingProvider,
        vector_index,
    ):
        self.repository = repository
        self.embedding_provider = embedding_provider
        self.vector_index = vector_index

    @staticmethod
    def _to_item(row) -> MemoryItem:
        return MemoryItem(
            id=row.id,
            user_id=row.user_id,
            text=row.text,
            tags=row.tags,
            created_at=row.created_at,
            updated_at=row.updated_at,
            metadata=row.metadata,
        )

    def add_memory(
        self,
        user_id: str,
        text: str,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> MemoryItem:
        memory_id = uuid.uuid4().hex
        row = self.repository.add(
            memory_id=memory_id,
            user_id=user_id,
            text=text,
            tags=tags or [],
            metadata=metadata or {},
        )
        vector = self.embedding_provider.embed_text(text)
        self.vector_index.upsert(
            memory_id=memory_id,
            user_id=user_id,
            vector=vector,
            metadata={"id": memory_id},
        )
        return self._to_item(row)

    def list_memories(self, user_id: str) -> List[MemoryItem]:
        return [self._to_item(row) for row in self.repository.list_by_user(user_id)]

    def get_memory(self, memory_id: str) -> Optional[MemoryItem]:
        row = self.repository.get(memory_id)
        if row is None:
            return None
        return self._to_item(row)

    def update_memory(
        self,
        memory_id: str,
        text: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[MemoryItem]:
        updated = self.repository.update(memory_id, text=text, tags=tags, metadata=metadata)
        if updated is None:
            return None

        # Re-index when text changes.
        vector = self.embedding_provider.embed_text(updated.text)
        self.vector_index.upsert(
            memory_id=updated.id,
            user_id=updated.user_id,
            vector=vector,
            metadata={"id": updated.id},
        )
        return self._to_item(updated)

    def delete_memory(self, memory_id: str) -> bool:
        deleted = self.repository.delete(memory_id)
        if deleted:
            self.vector_index.delete(memory_id)
        return deleted

    def search_memories(self, user_id: str, query: str, top_k: int = 3) -> List[MemorySearchResult]:
        query_vector = self.embedding_provider.embed_text(query)
        hits: List[VectorSearchResult] = self.vector_index.search(
            user_id=user_id,
            query_vector=query_vector,
            top_k=top_k,
        )
        rows = self.repository.get_many([hit.memory_id for hit in hits])
        results = []
        for hit in hits:
            row = rows.get(hit.memory_id)
            if row is None:
                continue
            results.append(MemorySearchResult(memory=self._to_item(row), score=hit.score))
        return results

    def memory_context_text(self, user_id: str, query: str, top_k: int) -> str:
        results = self.search_memories(user_id=user_id, query=query, top_k=top_k)
        if not results:
            return ""
        lines = []
        for item in results:
            lines.append(f"- ({item.score:.3f}) {item.memory.text}")
        return "Relevant long-term memories:\n" + "\n".join(lines)

    def extract_and_store(self, user_id: str, user_message: str) -> Optional[MemoryItem]:
        """
        Rule-based memory extraction.
        Captures durable preferences and stable personal facts from user messages.
        """
        text = user_message.strip()
        if len(text) < 8:
            return None

        preference_patterns = [
            r"\bi prefer\b",
            r"\bmy preference is\b",
            r"\bi like\b",
            r"\bi dislike\b",
            r"\bplease always\b",
            r"\bplease never\b",
            r"\bcall me\b",
            r"\bmy name is\b",
        ]
        if not any(re.search(pattern, text.lower()) for pattern in preference_patterns):
            return None

        return self.add_memory(
            user_id=user_id,
            text=text,
            tags=["auto_extracted", "user_preference"],
            metadata={"source": "rule_extractor"},
        )


def build_memory_service(app_config: AppConfig, model_config: ModelConfig) -> MemoryService:
    persist_dir = Path(app_config.MEMORY_PERSIST_DIR)
    persist_dir.mkdir(parents=True, exist_ok=True)

    repository = MemoryRepository(db_path=str(persist_dir / "memory.db"))
    embeddings = EmbeddingProvider(
        base_url=model_config.base_url,
        api_key=model_config.api_key,
        embedding_model=app_config.EMBEDDING_MODEL,
        dimension=app_config.EMBEDDING_DIMENSION,
        use_remote=app_config.EMBEDDING_USE_REMOTE,
    )
    vector_index = build_vector_index(
        backend=app_config.MEMORY_VECTOR_BACKEND,
        persist_dir=str(persist_dir),
        collection_name=app_config.MEMORY_COLLECTION_NAME,
    )
    return MemoryService(
        repository=repository,
        embedding_provider=embeddings,
        vector_index=vector_index,
    )

