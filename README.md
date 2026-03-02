# Conversational AI System

Lightweight conversational AI stack with:

- FastAPI backend (LangGraph orchestration + universal OpenAI-compatible model client)
- Local-first memory system (short-term + long-term semantic memory)
- Custom React frontend (no Docker UI dependency)

## Architecture

`Frontend (React + Vite) -> FastAPI -> LangGraph -> UniversalChat -> OpenAI-compatible backend`

## Core Features

- Chat UI with local conversation history (browser localStorage)
- Model selection from backend `/api/v1/models` (fallback `/v1/models`)
- Prompt scene selector + optional system prompt input
- Memory panel:
  - list/add/delete memories
  - semantic memory search
- Trace drawer for last assistant response metadata
- OpenAI-compatible chat endpoints remain available:
  - `POST /api/v1/chat/completions`
  - `POST /v1/chat/completions`

## Project Structure

```text
backend/              FastAPI app + LangGraph + memory modules
frontend/             React + Vite + TypeScript frontend
tests/                Pytest backend tests
docs/MEMORY_SYSTEM.md Memory architecture/spec
docs/FRONTEND.md      Frontend architecture/extension notes
run_all.py            One-command dev runner (backend + frontend)
```

## Prerequisites

- Python 3.11+
- Node.js 18+ (includes npm)
- Conda env `servicebot` activated

## Setup

1. Install backend dependencies:

```bash
pip install -r requirements.txt
```

2. Install frontend dependencies:

```bash
cd frontend
npm install
cd ..
```

3. Configure backend env:

```bash
copy .env.example .env
```

Set at least:

- `MODEL_NAME`
- `BASE_URL`
- `API_KEY`
- `EMBEDDING_MODEL` (recommended: `text-embedding-v4`)
- `EMBEDDING_API_KEY` (or reuse `API_KEY`)

## Run Dev (One Command)

From project root:

```bash
python run_all.py
```

This starts:

- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`

## Frontend Configuration

Frontend reads:

- `VITE_API_BASE_URL` (default `http://localhost:8000`)

Example:

```bash
copy frontend\\.env.example frontend\\.env
```

## API Endpoints Used by Frontend

- Health: `GET /health`
- Models: `GET /api/v1/models` (fallback `GET /v1/models`)
- Chat: `POST /api/v1/chat/completions`
- Memory:
  - `POST /api/v1/memory`
  - `GET /api/v1/memory?user_id=...`
  - `DELETE /api/v1/memory/{memory_id}`
  - `POST /api/v1/memory/search`
- Prompt scenes:
  - `GET /api/v1/prompt-scenes`

## Verification

1. Start all services:

```bash
python run_all.py
```

2. Check backend health:

```bash
curl http://localhost:8000/health
```

3. Check models:

```bash
curl http://localhost:8000/api/v1/models
```

4. Open browser:

- `http://localhost:3000`

5. Chat test:

- Select model
- Send a user message
- Confirm assistant response appears

6. Memory test:

- Add memory in Memory panel
- Search memory in Memory panel
- Confirm stored items list updates

## Tests

Run backend tests:

```bash
pytest
```

Focused suites:

```bash
pytest tests/test_api.py tests/test_graph.py tests/test_memory_api.py tests/test_memory_store.py -q
```

## Frontend Build

```bash
cd frontend
npm run build
```

## Troubleshooting

- Port conflict:
  - Ensure `8000` and `3000` are free before `python run_all.py`.
- Backend up but no models in UI:
  - Verify `GET /api/v1/models` returns data.
- Memory panel empty:
  - Verify `.env` has memory enabled and backend logs show memory services initialized.
- Frontend cannot reach backend:
  - Check `frontend/.env` `VITE_API_BASE_URL` and browser devtools network errors.
