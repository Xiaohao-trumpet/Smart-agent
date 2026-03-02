"""Tests for memory CRUD/search API endpoints."""

from pathlib import Path
import shutil
import uuid
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from backend.main import app
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
        collection_name="test_memories_api",
    )
    return MemoryService(repository=repo, embedding_provider=embeddings, vector_index=index)


@pytest.fixture
def client_with_memory():
    base = (Path.cwd() / ".pytest_tmp").resolve()
    base.mkdir(parents=True, exist_ok=True)
    tmp_dir = base / f"memory_api_{uuid.uuid4().hex}"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    service = build_local_service(tmp_dir)
    try:
        with patch("backend.main.memory_service", service):
            with TestClient(app) as client:
                yield client
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def test_memory_api_crud(client_with_memory: TestClient):
    create_payload = {
        "user_id": "api_user",
        "text": "I prefer concise answers.",
        "tags": ["preference"],
        "metadata": {"source": "api"},
    }
    create_res = client_with_memory.post("/api/v1/memory", json=create_payload)
    assert create_res.status_code == 200
    memory = create_res.json()
    memory_id = memory["id"]
    assert memory["user_id"] == "api_user"

    list_res = client_with_memory.get("/api/v1/memory", params={"user_id": "api_user"})
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1

    get_res = client_with_memory.get(f"/api/v1/memory/{memory_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == memory_id

    update_res = client_with_memory.put(
        f"/api/v1/memory/{memory_id}",
        json={"text": "I prefer concise and direct answers."},
    )
    assert update_res.status_code == 200
    assert "direct" in update_res.json()["text"]

    search_res = client_with_memory.post(
        "/api/v1/memory/search",
        json={"user_id": "api_user", "query": "concise style", "top_k": 3},
    )
    assert search_res.status_code == 200
    hits = search_res.json()["hits"]
    assert hits
    assert hits[0]["memory"]["id"] == memory_id

    delete_res = client_with_memory.delete(f"/api/v1/memory/{memory_id}")
    assert delete_res.status_code == 200
