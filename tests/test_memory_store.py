"""Tests for long-term memory service and local vector search."""

from pathlib import Path
import shutil
import uuid

from backend.memory.embeddings import EmbeddingProvider
from backend.memory.repository import MemoryRepository
from backend.memory.service import MemoryService
from backend.memory.vector_index import build_vector_index


def build_local_service(tmp_path: Path) -> MemoryService:
    repo = MemoryRepository(db_path=str(tmp_path / "memory.db"))
    embeddings = EmbeddingProvider(
        base_url="http://localhost:8000/v1",
        api_key="dummy",
        embedding_model="local-fallback",
        dimension=128,
        use_remote=False,
    )
    index = build_vector_index(
        backend="local",
        persist_dir=str(tmp_path),
        collection_name="test_memories",
    )
    return MemoryService(repository=repo, embedding_provider=embeddings, vector_index=index)


def _make_local_tmp_dir() -> Path:
    base = (Path.cwd() / ".pytest_tmp").resolve()
    base.mkdir(parents=True, exist_ok=True)
    target = base / f"memory_store_{uuid.uuid4().hex}"
    target.mkdir(parents=True, exist_ok=True)
    return target


def test_memory_crud_and_search():
    tmp_dir = _make_local_tmp_dir()
    try:
        service = build_local_service(tmp_dir)

        created = service.add_memory(
            user_id="u1",
            text="I prefer concise answers.",
            tags=["preference"],
            metadata={"source": "manual"},
        )
        assert created.user_id == "u1"
        assert created.text.startswith("I prefer")

        listed = service.list_memories("u1")
        assert len(listed) == 1
        assert listed[0].id == created.id

        loaded = service.get_memory(created.id)
        assert loaded is not None
        assert loaded.text == "I prefer concise answers."

        updated = service.update_memory(created.id, text="I prefer concise and direct answers.")
        assert updated is not None
        assert "direct" in updated.text

        hits = service.search_memories(user_id="u1", query="concise response style", top_k=3)
        assert hits
        assert hits[0].memory.id == created.id

        deleted = service.delete_memory(created.id)
        assert deleted is True
        assert service.get_memory(created.id) is None
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def test_rule_based_memory_extraction():
    tmp_dir = _make_local_tmp_dir()
    try:
        service = build_local_service(tmp_dir)
        auto = service.extract_and_store(
            user_id="u2",
            user_message="Please always answer in bullet points and concise style.",
        )
        assert auto is not None
        assert "user_preference" in auto.tags
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
