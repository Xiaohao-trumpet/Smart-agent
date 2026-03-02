# Architecture Documentation

## System Architecture

This document provides detailed architecture information for the Phase 1 Conversational AI System.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         OpenWebUI                            │
│                    (External Frontend)                       │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Layer                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  • Request Validation (Pydantic)                     │   │
│  │  • Rate Limiting                                     │   │
│  │  • Error Handling                                    │   │
│  │  • Structured Logging                                │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   LangGraph Orchestration                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Phase 1: Entry → model_node → END                   │   │
│  │                                                       │   │
│  │  Future: Entry → memory → planner → tools →          │   │
│  │          model → reflection → END                    │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  UniversalChat Abstraction                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  • Conversation History Management                   │   │
│  │  • Message Formatting (OpenAI format)                │   │
│  │  • Multi-backend Support                             │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              OpenAI-Compatible Backends                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   Qwen   │  │  Ollama  │  │   vLLM   │  │  Others  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Frontend Layer (OpenWebUI)

**Responsibility**: User interface and interaction

**Key Features**:
- Chat interface
- Conversation history
- User authentication (optional)
- Model selection
- Settings management

**Integration**:
- Configured via environment variables
- Points to backend API endpoint
- No source code modifications required

### 2. API Layer (FastAPI)

**File**: `backend/main.py`

**Responsibilities**:
- HTTP request/response handling
- Input validation using Pydantic models
- Rate limiting (in-memory)
- Error handling and HTTP status codes
- Structured logging
- Dependency injection

**Key Endpoints**:
- `POST /api/v1/chat`: Main chat endpoint
- `GET /health`: Health check
- `POST /api/v1/chat/stream`: Streaming placeholder
- `DELETE /api/v1/session/{user_id}`: Session management

**Design Patterns**:
- Dependency injection for shared resources
- Middleware for CORS
- Centralized error handling
- Request/response models with Pydantic

### 3. Orchestration Layer (LangGraph)

**Files**: 
- `backend/agents/graph.py`
- `backend/agents/node_calls.py`

**Responsibilities**:
- Manage conversation flow
- Coordinate between different processing nodes
- State management
- Extensibility for future nodes

**Current Flow (Phase 1)**:
```python
Entry → model_node → END
```

**Future Flow (Phase 2+)**:
```python
Entry → memory_node → planner_node → tool_node → 
model_node → reflection_node → END
```

**State Structure**:
```python
class ChatState(TypedDict):
    user_id: str
    user_message: str
    response: Optional[str]
    # Future fields:
    # memories: List[Memory]
    # tools_used: List[ToolCall]
    # reward_score: float
    # plan: Plan
```

### 4. Model Abstraction Layer (UniversalChat)

**File**: `backend/models/universal_chat.py`

**Responsibilities**:
- Unified interface to OpenAI-compatible backends
- Conversation history management
- Message formatting
- Backend-agnostic API

**Key Methods**:
- `chat()`: Synchronous chat
- `astream()`: Async streaming (placeholder)
- `clear_history()`: Clear conversation
- `get_history()`: Retrieve history

**Supported Backends**:
- Qwen (cloud API)
- Ollama (local)
- vLLM (local)
- Any OpenAI-compatible server

**Design Benefits**:
- Easy backend switching via configuration
- No code changes required
- Testable with mocks
- Extensible for future features

### 5. Configuration Layer

**File**: `backend/config.py`

**Responsibilities**:
- Centralized configuration
- Environment variable handling
- Default values
- Configuration validation

**Configuration Classes**:
- `ModelConfig`: Model-specific settings
- `AppConfig`: Application-level settings

### 6. Session Management

**File**: `backend/session_store.py`

**Responsibilities**:
- User session tracking
- Conversation history storage
- TTL-based expiration
- Session cleanup

**Current Implementation**:
- In-memory storage
- Thread-safe operations
- Automatic expiration

**Future Enhancement**:
- Redis backend
- Distributed session support
- Persistent storage

### 7. Prompt Management

**Files**:
- `backend/prompts/prompt_factory.py`
- `backend/prompts/*.txt`

**Responsibilities**:
- Externalize prompts from code
- Support multiple scenarios
- Template variable substitution (future)
- Prompt caching

**Scenarios**:
- `default`: General assistant
- `it_helpdesk`: IT support scenario

### 8. Utilities

**Logging** (`backend/utils/logging.py`):
- Structured JSON logging
- Text format support
- Custom log fields
- Request/response logging

**Exceptions** (`backend/utils/exceptions.py`):
- Custom exception hierarchy
- Specific error types
- Better error handling

## Data Flow

### Chat Request Flow

1. **User Input** → OpenWebUI
2. **HTTP Request** → FastAPI `/api/v1/chat`
3. **Validation** → Pydantic models
4. **Rate Limiting** → Check user limits
5. **Session Management** → Create/retrieve session
6. **Graph Invocation** → LangGraph processes request
7. **Model Call** → UniversalChat.chat()
8. **API Call** → OpenAI-compatible backend
9. **Response Processing** → Extract and format response
10. **Logging** → Record request details
11. **HTTP Response** → Return to OpenWebUI
12. **Display** → Show to user

### State Management

```python
# Initial state
{
    "user_id": "user123",
    "user_message": "Hello",
    "response": None
}

# After model_node
{
    "user_id": "user123",
    "user_message": "Hello",
    "response": "Hi! How can I help you?"
}
```

## Extension Points

### Adding Memory (Phase 2)

1. Create `memory_node` in `node_calls.py`
2. Add memory fields to `ChatState`
3. Integrate memory store (Redis/Vector DB)
4. Update graph flow: `memory_node → model_node`

### Adding Tools (Phase 2)

1. Create `tool_node` in `node_calls.py`
2. Implement tool registry
3. Add tool parsing logic
4. Update graph flow: `model_node → tool_node → model_node`

### Adding Reflection (Phase 2)

1. Create `reflection_node` in `node_calls.py`
2. Implement quality checker
3. Add reward scoring
4. Update graph flow: `model_node → reflection_node → END`

### Adding Streaming (Phase 2)

1. Implement `astream()` in UniversalChat
2. Update FastAPI endpoint for SSE
3. Handle partial responses
4. Update OpenWebUI configuration

## Security Considerations

### Current Implementation

- Rate limiting per user
- Input validation with Pydantic
- Error message sanitization
- CORS configuration

### Future Enhancements

- API key authentication
- JWT tokens
- Request signing
- Input sanitization
- SQL injection prevention
- XSS protection

## Performance Considerations

### Current Optimizations

- In-memory session storage
- Prompt caching
- Connection pooling (OpenAI client)

### Future Optimizations

- Redis for session storage
- Response caching
- Request batching
- Async processing
- Load balancing
- Horizontal scaling

## Testing Strategy

### Unit Tests

- Model abstraction (mocked API)
- Graph nodes (mocked dependencies)
- Session store
- Prompt factory

### Integration Tests

- API endpoints (TestClient)
- End-to-end flow
- Error handling

### Future Testing

- Load testing
- Stress testing
- Security testing
- A/B testing framework

## Deployment

### Development

```bash
python run_backend.py
```

### Production (Docker)

```bash
docker-compose -f frontend/docker-compose.yml up -d
```

### Scaling Considerations

- Stateless API design
- External session storage (Redis)
- Load balancer
- Multiple backend instances
- Database connection pooling

## Monitoring and Observability

### Current Logging

- Structured JSON logs
- Request/response logging
- Error tracking
- Latency measurement

### Future Enhancements

- Prometheus metrics
- Grafana dashboards
- Distributed tracing (OpenTelemetry)
- Error tracking (Sentry)
- Log aggregation (ELK stack)

## Configuration Management

### Environment Variables

All configuration via `.env` file:
- Model settings
- Server settings
- Logging configuration
- Rate limiting
- Session management

### Future Enhancements

- Configuration service
- Feature flags
- A/B testing configuration
- Dynamic configuration updates
