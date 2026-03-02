# Project Index - Quick Navigation

Welcome to the Phase 1 Conversational AI System! This index helps you quickly find what you need.

## 🚀 Getting Started

1. **First Time Setup**: [QUICKSTART.md](QUICKSTART.md)
   - 5-minute setup guide
   - Step-by-step instructions
   - Common commands

2. **Verify Installation**: Run `python verify_setup.py`
   - Checks all files and dependencies
   - Validates Python version
   - Confirms environment setup

3. **Configuration**: [.env.example](.env.example)
   - Copy to `.env`
   - Set your API key
   - Adjust settings as needed

## 📖 Documentation

### Main Documentation
- **[README.md](README.md)** - Complete project documentation
  - Project overview
  - Setup instructions
  - API reference
  - Configuration options
  - Troubleshooting

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture
  - High-level design
  - Component details
  - Data flow
  - Extension points

- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Implementation summary
  - What's implemented
  - File structure
  - Key features
  - Success criteria

### Development
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines
  - Code style
  - Testing requirements
  - Pull request process
  - Common tasks

## 🏗️ Code Structure

### Backend (`backend/`)

#### Core Files
- **[main.py](backend/main.py)** - FastAPI application
  - API endpoints
  - Request/response handling
  - Error handling
  - Rate limiting

- **[config.py](backend/config.py)** - Configuration
  - ModelConfig class
  - AppConfig class
  - Environment variables

- **[session_store.py](backend/session_store.py)** - Session management
  - In-memory storage
  - TTL support
  - Thread-safe operations

#### Modules

**Agents (`backend/agents/`)**
- **[graph.py](backend/agents/graph.py)** - LangGraph definition
  - ChatState type
  - Graph creation
  - Extension points

- **[node_calls.py](backend/agents/node_calls.py)** - Node implementations
  - model_node (Phase 1)
  - Future nodes (placeholders)

**Models (`backend/models/`)**
- **[universal_chat.py](backend/models/universal_chat.py)** - Model abstraction
  - UniversalChat class
  - OpenAI-compatible interface
  - Conversation history

**Prompts (`backend/prompts/`)**
- **[prompt_factory.py](backend/prompts/prompt_factory.py)** - Prompt loader
  - PromptFactory class
  - Caching mechanism

- **[system.txt](backend/prompts/system.txt)** - Default prompt
- **[it_helpdesk.txt](backend/prompts/it_helpdesk.txt)** - IT helpdesk prompt

**Utils (`backend/utils/`)**
- **[logging.py](backend/utils/logging.py)** - Structured logging
  - JSONFormatter
  - setup_logging()

- **[exceptions.py](backend/utils/exceptions.py)** - Custom exceptions
  - Exception hierarchy
  - Specific error types

### Frontend (`frontend/`)
- **[docker-compose.yml](frontend/docker-compose.yml)** - Full stack deployment
  - Backend service
  - OpenWebUI service
  - Network configuration

### Tests (`tests/`)
- **[conftest.py](tests/conftest.py)** - Shared fixtures
- **[test_api.py](tests/test_api.py)** - API endpoint tests
- **[test_graph.py](tests/test_graph.py)** - LangGraph tests
- **[test_universal_chat.py](tests/test_universal_chat.py)** - Model tests
- **[test_session_store.py](tests/test_session_store.py)** - Session tests
- **[test_prompt_factory.py](tests/test_prompt_factory.py)** - Prompt tests
- **[test_config.py](tests/test_config.py)** - Configuration tests

## 🛠️ Utility Scripts

- **[run_backend.py](run_backend.py)** - Start the backend server
  ```bash
  python run_backend.py
  ```

- **[run_tests.py](run_tests.py)** - Run tests with options
  ```bash
  python run_tests.py          # All tests
  python run_tests.py coverage # With coverage
  python run_tests.py fast     # Fast tests only
  ```

- **[verify_setup.py](verify_setup.py)** - Verify installation
  ```bash
  python verify_setup.py
  ```

## 📦 Configuration Files

- **[requirements.txt](requirements.txt)** - Python dependencies
- **[Dockerfile](Dockerfile)** - Container definition
- **[pytest.ini](pytest.ini)** - Pytest configuration
- **[.gitignore](.gitignore)** - Git ignore rules
- **[.env.example](.env.example)** - Environment template

## 🔍 Quick Reference

### Common Tasks

**Start Backend**
```bash
python run_backend.py
```

**Run Tests**
```bash
pytest
# or
python run_tests.py
```

**Start Full Stack**
```bash
cd frontend
docker-compose up -d
```

**Test API**
```bash
curl http://localhost:8000/health
```

**Chat Request**
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "message": "Hello"}'
```

### Key Endpoints

- `GET /health` - Health check
- `POST /api/v1/chat` - Chat endpoint
- `POST /api/v1/chat/stream` - Streaming (placeholder)
- `DELETE /api/v1/session/{user_id}` - Delete session
- `GET /docs` - API documentation (Swagger)

### Environment Variables

**Required:**
- `API_KEY` - Your model API key

**Optional (with defaults):**
- `MODEL_NAME` - Model to use (default: qwen-plus)
- `BASE_URL` - API endpoint URL
- `DEFAULT_TEMPERATURE` - Sampling temperature (default: 0.7)
- `DEFAULT_MAX_TOKENS` - Max tokens (default: 1024)
- `SYSTEM_PROMPT_SCENE` - Prompt scenario (default: default)
- `LOG_LEVEL` - Logging level (default: INFO)
- `PORT` - Server port (default: 8000)

See [.env.example](.env.example) for complete list.

## 🎯 Use Cases

### Switching Model Backends

**Qwen (Cloud)**
```env
MODEL_NAME=qwen-plus
BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
API_KEY=your_key
```

**Ollama (Local)**
```env
MODEL_NAME=llama3
BASE_URL=http://localhost:11434/v1
API_KEY=dummy
```

**vLLM (Local)**
```env
MODEL_NAME=your-model
BASE_URL=http://localhost:8000/v1
API_KEY=dummy
```

### Adding Custom Prompts

1. Create `backend/prompts/my_prompt.txt`
2. Add content
3. Set `SYSTEM_PROMPT_SCENE=my_prompt`
4. Restart backend

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_api.py

# With coverage
pytest --cov=backend

# Verbose
pytest -v

# Using test runner
python run_tests.py coverage
```

## 🔗 External Resources

- **OpenWebUI**: https://github.com/open-webui/open-webui
- **FastAPI**: https://fastapi.tiangolo.com/
- **LangGraph**: https://langchain-ai.github.io/langgraph/
- **Pydantic**: https://docs.pydantic.dev/

## 📊 Project Status

✅ Phase 1 Complete
- End-to-end chat system
- Clean architecture
- OpenWebUI integration
- Comprehensive documentation
- Full test coverage

🔜 Phase 2 Planned
- Memory system
- Tool calling
- RL optimization
- Streaming support

## 🆘 Getting Help

1. Check [QUICKSTART.md](QUICKSTART.md) for setup issues
2. Review [README.md](README.md) troubleshooting section
3. Run `python verify_setup.py` to check installation
4. Check logs for error messages
5. Review [ARCHITECTURE.md](ARCHITECTURE.md) for design questions

## 📝 Notes

- This is a Phase 1 implementation
- Designed for extensibility
- Production-ready patterns
- No OpenWebUI modifications required
- Easy backend switching via configuration

---

**Quick Links:**
[README](README.md) | [Quick Start](QUICKSTART.md) | [Architecture](ARCHITECTURE.md) | [Contributing](CONTRIBUTING.md) | [Summary](PROJECT_SUMMARY.md)
