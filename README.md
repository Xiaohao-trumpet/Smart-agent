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
- Phase 3 tool calling with planner + safe executor (kb + tickets)
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

## Phase 3: Tool Calling & Automated Prompts

What it does:

- Adds intent routing and ReAct-style tool planning before final response generation.
- Executes local-first tools safely (allowlist, timeout, rate limit).
- Builds final prompt dynamically from memory + tool context + user message.
- Keeps OpenWebUI compatibility (`/v1/models`, `/v1/chat/completions`) while running tools internally.

Enable/disable tools:

- Set `TOOLS_ENABLED=true|false` in `.env`.

Configure tool storage paths:

- `KB_FILE_PATH=./data/kb/faq.json`
- `TICKET_DB_PATH=./data/tickets/tickets.db`

Add a new tool:

1. Add schema models in `backend/tools/schemas.py`.
2. Implement and register the tool in `backend/tools/builtin.py`.
3. Add tool name to `TOOLS_ALLOWLIST`.
4. Extend `backend/tools/planner.py` routing logic if auto-selection is needed.
5. Add focused tests in `tests/`.

### Demo via curl

Create ticket:

```bash
curl -X POST http://localhost:8000/v1/chat/completions ^
  -H "Content-Type: application/json" ^
  -d "{\"model\":\"qwen-plus\",\"user\":\"demo_user\",\"messages\":[{\"role\":\"user\",\"content\":\"I want to open a support ticket for my internet not working\"}]}"
```

KB policy query:

```bash
curl -X POST http://localhost:8000/v1/chat/completions ^
  -H "Content-Type: application/json" ^
  -d "{\"model\":\"qwen-plus\",\"user\":\"demo_user\",\"messages\":[{\"role\":\"user\",\"content\":\"What is your refund policy?\"}]}"
```

Inspect trace with internal chat endpoint:

```bash
curl -X POST http://localhost:8000/api/v1/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"user_id\":\"demo_user\",\"message\":\"I want to open a support ticket for my internet not working\"}"
```

### Demo via OpenWebUI

1. Keep OpenWebUI pointing to this backend OpenAI-compatible base URL.
2. Start chat in browser and ask:
   - `I want to open a support ticket for my internet not working`
   - `What is your refund policy?`
3. Backend internally plans and executes tools; OpenWebUI remains unaware of internal tool mechanics.
4. If OpenWebUI sends `stream=true`, backend currently returns a single content chunk and `[DONE]`.

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
