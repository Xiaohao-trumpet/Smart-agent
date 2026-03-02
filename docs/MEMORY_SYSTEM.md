# Memory System Spec (Phase 2)

## 1. Overview

Phase 2 adds a production-minded memory layer while preserving the existing architecture:

`FastAPI API Layer -> LangGraph Orchestration -> UniversalChat Model Client`

Memory capabilities:

- Short-term memory: session-level context with sliding window and optional summary compaction.
- Long-term memory: local persistent store with semantic retrieval by user and query.
- Full CRUD API for memory management.
- LangGraph integration:
  - pre-model retrieval and prompt injection
  - post-model optional memory extraction/write

## 2. Architecture

### 2.1 Components

- `backend/memory/short_term.py`
  - Sliding-window context policy.
  - Optional summary compaction after threshold turns.

- `backend/memory/repository.py`
  - SQLite persistence for memory records.
  - CRUD and list-by-user APIs.

- `backend/memory/embeddings.py`
  - OpenAI-compatible embeddings call support.
  - Deterministic local fallback embedding when remote embeddings are unavailable.

- `backend/memory/vector_index.py`
  - Chroma-backed vector index (preferred local persistent backend).
  - Local file-based vector index fallback if Chroma is unavailable.

- `backend/memory/service.py`
  - High-level memory service for CRUD/search.
  - Rule-based automatic extraction of durable user preferences.

### 2.2 LangGraph Flow

Current flow in Phase 2:

`Entry -> memory_retrieve -> model -> memory_write -> END`

- `memory_retrieve`
  - Loads short-term context from session.
  - Runs long-term semantic search.
  - Injects retrieved context into model input.

- `model`
  - Calls `UniversalChat` with memory-enriched message.

- `memory_write`
  - Appends turn to short-term session memory.
  - Optionally extracts and stores durable preferences.

## 3. Data Model

Memory record fields:

- `id`: string UUID-like identifier
- `user_id`: owner user identifier
- `text`: memory text
- `tags`: optional string list
- `created_at`: unix timestamp
- `updated_at`: unix timestamp
- `metadata`: JSON object

Persistence:

- SQLite file: `${MEMORY_PERSIST_DIR}/memory.db`
- Vector data:
  - Chroma persistence under `${MEMORY_PERSIST_DIR}` (preferred)
  - fallback local vector file `${MEMORY_PERSIST_DIR}/vectors.json`

## 4. Retrieval and Injection Strategy

1. Incoming user message arrives.
2. Short-term context built:
   - recent `N` turns
   - optional compacted summary
3. Long-term search:
   - filter by `user_id`
   - semantic query from current user message
   - top-k results returned
4. Prompt injection:
   - short-term summary/recent context
   - long-term memory snippets with similarity score
   - current user message

## 5. Memory APIs

Base: `/api/v1`

### 5.1 Add

`POST /api/v1/memory`

```bash
curl -X POST http://localhost:8000/api/v1/memory \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "text": "I prefer concise answers.",
    "tags": ["preference"],
    "metadata": {"source": "manual"}
  }'
```

### 5.2 List

`GET /api/v1/memory?user_id=user123`

### 5.3 Get by ID

`GET /api/v1/memory/{memory_id}`

### 5.4 Update

`PUT /api/v1/memory/{memory_id}`

```bash
curl -X PUT http://localhost:8000/api/v1/memory/<memory_id> \
  -H "Content-Type: application/json" \
  -d '{"text": "I prefer concise and direct answers."}'
```

### 5.5 Delete

`DELETE /api/v1/memory/{memory_id}`

### 5.6 Semantic Search

`POST /api/v1/memory/search`

```bash
curl -X POST http://localhost:8000/api/v1/memory/search \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "query": "How should the assistant answer me?",
    "top_k": 3
  }'
```

## 6. Configuration

Memory env vars:

- `MEMORY_ENABLED=true|false`
- `LONG_TERM_MEMORY_ENABLED=true|false`
- `MEMORY_WRITE_ENABLED=true|false`
- `SHORT_TERM_WINDOW_TURNS=6`
- `SHORT_TERM_ENABLE_SUMMARY=true|false`
- `SHORT_TERM_SUMMARY_TRIGGER_TURNS=10`
- `SHORT_TERM_SUMMARY_MAX_CHARS=800`
- `MEMORY_PERSIST_DIR=./data/memory`
- `MEMORY_VECTOR_BACKEND=chroma|local`
- `MEMORY_COLLECTION_NAME=user_memories`
- `MEMORY_SEARCH_TOP_K=3`
- `EMBEDDING_MODEL=text-embedding-3-small`
- `EMBEDDING_DIMENSION=256`
- `EMBEDDING_USE_REMOTE=true|false`

## 7. Operations

- Local-first: no Redis/Postgres required in Phase 2.
- Backups:
  - backup `${MEMORY_PERSIST_DIR}/memory.db`
  - backup vector persistence under `${MEMORY_PERSIST_DIR}`
- Restore:
  - restore both SQLite and vector files together for consistent search behavior.

## 8. Security and Privacy

- Memory stores user-provided text and metadata.
- Treat memory as potentially sensitive data.
- Use deletion API to support user data removal workflows.
- Consider retention policy and periodic cleanup for production.
- Avoid storing secrets/PII unless explicitly required and governed.

## 9. Extension Points

- Replace SQLite repository with Postgres repository implementation.
- Replace local/chroma vector index with managed vector DB.
- Replace rule-based extractor with model-based extraction classifier.
- Add per-tenant namespaces, retention policies, and encryption-at-rest.

