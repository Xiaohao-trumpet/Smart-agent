# Conversational AI System - Phase 1

A foundational conversational chatbot system with clean, extensible architecture built for future enhancements including agent memory, tool calling, and RL-style optimization.

## Project Overview

This is Phase 1 of an agentic customer support chatbot platform. The system provides:

- **End-to-end chat system** with HTTP API endpoints
- **Clean, layered architecture** with clear extension points
- **Plug-and-play model abstraction** supporting multiple OpenAI-compatible backends
- **OpenWebUI integration** as a ready-made frontend
- **Structured logging and configuration management**
- **Externalized prompt management**

### Architecture Layers

```
OpenWebUI (Frontend)
    ↓
FastAPI (API Layer)
    ↓
LangGraph (Orchestration Layer)
    ↓
UniversalChat (Model Abstraction)
    ↓
OpenAI-compatible Backend (Qwen/Ollama/vLLM)
```

## Technology Stack

- **Language**: Python 3.11+
- **Web Framework**: FastAPI
- **Orchestration**: LangGraph
- **Model Client**: OpenAI-compatible HTTP API
- **Logging**: Python logging with JSON support
- **Testing**: pytest
- **Server**: uvicorn

## Project Structure

```
project_root/
├── backend/
│   ├── __init__.py
│   ├── main.py              # FastAPI entrypoint and API routes
│   ├── config.py            # Configuration and model defaults
│   ├── session_store.py     # In-memory session handling
│   ├── prompts/
│   │   ├── system.txt       # Default system prompt
│   │   ├── it_helpdesk.txt  # IT helpdesk scenario prompt
│   │   └── prompt_factory.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── graph.py         # LangGraph graph definition
│   │   └── node_calls.py    # Node implementations
│   ├── models/
│   │   ├── __init__.py
│   │   └── universal_chat.py  # Model abstraction class
│   └── utils/
│       ├── logging.py       # Logging setup
│       └── exceptions.py    # Custom exception types
├── frontend/
│   └── docker-compose.yml   # OpenWebUI and backend services
├── tests/
│   ├── test_universal_chat.py
│   ├── test_graph.py
│   ├── test_session_store.py
│   └── test_api.py
├── requirements.txt
├── Dockerfile
├── .env.example
└── README.md
```

## Setup Instructions

### Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose (for OpenWebUI)
- API key for your chosen model backend (e.g., Qwen API key)

### 1. Clone and Setup Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
# Required: Set your API_KEY
```

Example `.env` configuration:

```env
# For Qwen
MODEL_NAME=qwen-plus
BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
API_KEY=your_qwen_api_key_here

# For local Ollama
# MODEL_NAME=llama3-8b
# BASE_URL=http://localhost:11434/v1
# API_KEY=dummy

# For local vLLM
# MODEL_NAME=your-model-name
# BASE_URL=http://localhost:8000/v1
# API_KEY=dummy
```

### 3. Run the Backend

```bash
# Development mode with auto-reload
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Or using Python directly
python -m backend.main
```

The backend API will be available at `http://localhost:8000`

### 4. Test the Backend

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend tests/

# Run specific test file
pytest tests/test_api.py -v
```

## OpenWebUI Integration

OpenWebUI (https://github.com/open-webui/open-webui) is used as the frontend without any modifications.

### Option 1: Using Docker Compose (Recommended)

```bash
cd frontend
docker-compose up -d
```

This will start:
- Backend API on `http://localhost:8000`
- OpenWebUI on `http://localhost:3000`

### Option 2: Manual OpenWebUI Setup

```bash
# Pull and run OpenWebUI
docker run -d \
  -p 3000:8080 \
  -e OPENAI_API_BASE_URL=http://localhost:8000/api/v1 \
  -e OPENAI_API_KEY=dummy \
  -e WEBUI_AUTH=false \
  --name openwebui \
  ghcr.io/open-webui/open-webui:main
```

### Accessing OpenWebUI

1. Open browser to `http://localhost:3000`
2. The UI will automatically connect to the backend
3. Start chatting!

### OpenWebUI Configuration

Key environment variables for OpenWebUI:

- `OPENAI_API_BASE_URL`: Points to backend API (`http://backend:8000/api/v1`)
- `OPENAI_API_KEY`: Can be dummy for local backends
- `WEBUI_AUTH`: Set to `false` for development (no authentication)

## API Reference

### POST /api/v1/chat

Synchronous chat endpoint for processing user messages.

**Request Body:**
```json
{
  "user_id": "string (required)",
  "message": "string (required)",
  "temperature": 0.7,  // optional, 0.0-2.0
  "max_tokens": 1024   // optional, 1-4096
}
```

**Response:**
```json
{
  "response": "Assistant's reply",
  "latency_ms": 123.45
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "message": "Hello, how can you help me?"
  }'
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "model_name": "qwen-plus",
  "active_sessions": 5
}
```

### POST /api/v1/chat/stream

Streaming endpoint (placeholder for Phase 2+).

**Response:**
```json
{
  "status": "not_implemented",
  "message": "Streaming support will be added in Phase 2"
}
```

### DELETE /api/v1/session/{user_id}

Delete a user session and clear conversation history.

**Response:**
```json
{
  "status": "success",
  "message": "Session deleted for user {user_id}"
}
```

## Architecture Overview

### 1. Frontend Layer (OpenWebUI)

- External project, not modified
- Provides chat UI, user management, conversation history
- Configured to point to our backend API

### 2. API Layer (FastAPI)

- HTTP request handling and validation
- Rate limiting (60 requests per 60 seconds per user)
- Error handling with appropriate HTTP status codes
- Structured logging for all requests
- Dependency injection for shared resources

### 3. Orchestration Layer (LangGraph)

**Current (Phase 1):**
- Single `model_node` that calls the LLM
- Simple flow: Entry → model_node → END

**Future Extension Points:**
- `memory_node`: Read/write short-term and long-term memory
- `tool_node`: Call external tools/APIs
- `reflection_node`: Quality checking and self-evaluation
- `planner_node`: Multi-step reasoning and plan generation

### 4. Model Abstraction Layer (UniversalChat)

Unified interface to OpenAI-compatible backends:

- **Qwen**: Cloud API with OpenAI-compatible endpoint
- **Ollama**: Local models with OpenAI-compatible API
- **vLLM**: High-performance local inference server
- **Any OpenAI-compatible server**

Features:
- Per-user conversation history (in-memory)
- Automatic message formatting
- Temperature and max_tokens control
- Placeholder for streaming, token counting, cost estimation

### 5. Configuration & State Layer

- Centralized configuration via `config.py`
- Environment variable support
- In-memory session store with TTL
- Future: Redis or database backend

### 6. Prompt Management Layer

- Externalized prompts in `prompts/` directory
- Prompt factory for loading and formatting
- Support for different scenarios (default, IT helpdesk, etc.)
- Easy customization without code changes

## Configuration Options

All configuration via environment variables:

### Model Configuration
- `MODEL_NAME`: Model identifier (default: `qwen-plus`)
- `BASE_URL`: OpenAI-compatible endpoint URL
- `API_KEY`: API key for authentication
- `DEFAULT_TEMPERATURE`: Sampling temperature (default: `0.7`)
- `DEFAULT_MAX_TOKENS`: Max tokens to generate (default: `1024`)
- `SYSTEM_PROMPT_SCENE`: Prompt scenario (default: `default`)

### Server Configuration
- `HOST`: Server host (default: `0.0.0.0`)
- `PORT`: Server port (default: `8000`)

### Logging Configuration
- `LOG_LEVEL`: Logging level (default: `INFO`)
- `LOG_FORMAT`: Format type - `json` or `text` (default: `json`)

### Session Configuration
- `SESSION_TTL_SECONDS`: Session timeout (default: `3600`)
- `SESSION_CLEANUP_INTERVAL`: Cleanup interval (default: `300`)

### Rate Limiting
- `RATE_LIMIT_REQUESTS`: Max requests (default: `60`)
- `RATE_LIMIT_WINDOW_SECONDS`: Time window (default: `60`)

### CORS Configuration
- `CORS_ORIGINS`: Allowed origins (default: `*`)

## Switching Model Backends

### Using Qwen (Cloud)

```env
MODEL_NAME=qwen-plus
BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
API_KEY=your_qwen_api_key
```

### Using Ollama (Local)

```bash
# Start Ollama
ollama serve

# Pull a model
ollama pull llama3

# Configure backend
MODEL_NAME=llama3
BASE_URL=http://localhost:11434/v1
API_KEY=dummy
```

### Using vLLM (Local)

```bash
# Start vLLM server
python -m vllm.entrypoints.openai.api_server \
  --model meta-llama/Llama-2-7b-chat-hf \
  --port 8000

# Configure backend
MODEL_NAME=meta-llama/Llama-2-7b-chat-hf
BASE_URL=http://localhost:8000/v1
API_KEY=dummy
```

## Development

### Running Tests

```bash
# All tests
pytest

# With verbose output
pytest -v

# Specific test file
pytest tests/test_api.py

# With coverage report
pytest --cov=backend --cov-report=html tests/
```

### Code Style

- Follow PEP 8
- Use type hints everywhere
- Use Google-style docstrings
- Keep functions focused and testable

### Adding New Prompts

1. Create a new `.txt` file in `backend/prompts/`
2. Add the prompt content
3. Update `prompt_factory.py` filename mapping if needed
4. Set `SYSTEM_PROMPT_SCENE` environment variable

## Future Work (Phase 2+)

### Memory System
- Short-term memory: Recent conversation context
- Long-term memory: User preferences, past interactions
- Vector database integration for semantic search

### Tool Calling
- External API integration
- Database queries
- File system operations
- Custom tool registry

### RL-Style Optimization
- Response quality evaluation
- Reward scoring
- Feedback loops for continuous improvement
- A/B testing framework

### Streaming Support
- Real-time token streaming
- Server-sent events (SSE)
- WebSocket support
- Improved user experience for long responses

### Enhanced Persistence
- Redis for session storage
- PostgreSQL for conversation history
- Vector database for memory retrieval

## Troubleshooting

### Backend won't start

- Check Python version: `python --version` (must be 3.11+)
- Verify all dependencies installed: `pip install -r requirements.txt`
- Check environment variables in `.env`
- Verify API key is valid

### OpenWebUI can't connect to backend

- Ensure backend is running: `curl http://localhost:8000/health`
- Check `OPENAI_API_BASE_URL` in docker-compose.yml
- Verify network connectivity between containers
- Check Docker logs: `docker logs openwebui`

### Model API errors

- Verify API key is correct
- Check BASE_URL is accessible
- Test with curl: `curl -X POST $BASE_URL/chat/completions ...`
- Check model name is valid for your backend

### Rate limiting issues

- Adjust `RATE_LIMIT_REQUESTS` and `RATE_LIMIT_WINDOW_SECONDS`
- Clear rate limit by restarting backend
- Implement Redis-based rate limiting for production

## License

This project is provided as-is for educational and development purposes.

## Support

For issues and questions:
1. Check this README
2. Review the code documentation
3. Check logs for error messages
4. Test with curl to isolate issues
