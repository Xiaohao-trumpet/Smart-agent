"""
FastAPI application entrypoint.
Provides HTTP API endpoints for the conversational AI system.
"""

import time
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import logging

from .config import get_model_config, get_app_config
from .models.universal_chat import UniversalChat
from .agents.graph import create_chat_graph
from .session_store import get_session_store
from .prompts.prompt_factory import get_prompt_factory
from .utils.logging import setup_logging, get_logger
from .utils.exceptions import (
    ModelAPIException,
    RateLimitExceededException,
    ValidationException
)

# Initialize configuration
app_config = get_app_config()
model_config = get_model_config()

# Setup logging
setup_logging(log_level=app_config.LOG_LEVEL, log_format=app_config.LOG_FORMAT)
logger = get_logger(__name__)

# Global instances (initialized in lifespan)
model_client: Optional[UniversalChat] = None
chat_graph = None
session_store = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global model_client, chat_graph, session_store
    
    logger.info("Starting application...")
    
    # Initialize prompt factory and load system prompt
    prompt_factory = get_prompt_factory()
    system_prompt = prompt_factory.get_system_prompt(model_config.system_prompt_scene)
    
    # Initialize model client
    model_client = UniversalChat(
        model_name=model_config.model_name,
        base_url=model_config.base_url,
        api_key=model_config.api_key,
        system_prompt=system_prompt,
        default_temperature=model_config.default_temperature,
        default_max_tokens=model_config.default_max_tokens
    )
    logger.info(f"Initialized model client: {model_config.model_name}")
    
    # Initialize chat graph
    chat_graph = create_chat_graph(model_client)
    logger.info("Initialized chat graph")
    
    # Initialize session store
    session_store = get_session_store(ttl_seconds=app_config.SESSION_TTL_SECONDS)
    logger.info("Initialized session store")
    
    yield
    
    logger.info("Shutting down application...")


# Create FastAPI app
app = FastAPI(
    title="Conversational AI System",
    description="Phase 1: Foundational chatbot with extensible architecture",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=app_config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Rate limiting storage (simple in-memory)
rate_limit_store = {}


def check_rate_limit(user_id: str) -> None:
    """Simple rate limiting check."""
    current_time = time.time()
    window_start = current_time - app_config.RATE_LIMIT_WINDOW_SECONDS
    
    # Clean old entries
    if user_id in rate_limit_store:
        rate_limit_store[user_id] = [
            ts for ts in rate_limit_store[user_id] if ts > window_start
        ]
    else:
        rate_limit_store[user_id] = []
    
    # Check limit
    if len(rate_limit_store[user_id]) >= app_config.RATE_LIMIT_REQUESTS:
        raise RateLimitExceededException(
            f"Rate limit exceeded: {app_config.RATE_LIMIT_REQUESTS} requests per "
            f"{app_config.RATE_LIMIT_WINDOW_SECONDS} seconds"
        )
    
    # Add current request
    rate_limit_store[user_id].append(current_time)


# Request/Response models
class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    user_id: str = Field(..., description="User identifier")
    message: str = Field(..., min_length=1, description="User message")
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: Optional[int] = Field(None, ge=1, le=4096, description="Maximum tokens to generate")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str = Field(..., description="Assistant's response")
    latency_ms: float = Field(..., description="End-to-end processing time in milliseconds")


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    model_name: str
    active_sessions: int


# Endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="ok",
        model_name=model_config.model_name,
        active_sessions=session_store.get_session_count()
    )


@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Synchronous chat endpoint.
    
    Processes a user message and returns the assistant's response.
    """
    start_time = time.time()
    
    try:
        # Rate limiting
        check_rate_limit(request.user_id)
        
        # Create or get session
        session = session_store.create_session(request.user_id)
        
        # Prepare state for graph
        state = {
            "user_id": request.user_id,
            "user_message": request.message,
            "response": None
        }
        
        # Invoke the chat graph
        result = chat_graph.invoke(state)
        
        # Extract response
        response_text = result.get("response", "")
        
        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000
        
        # Log request
        logger.info(
            "Chat request processed",
            extra={
                "user_id": request.user_id,
                "endpoint": "/api/v1/chat",
                "latency_ms": latency_ms,
                "status": "success",
                "model_name": model_config.model_name
            }
        )
        
        return ChatResponse(
            response=response_text,
            latency_ms=latency_ms
        )
    
    except RateLimitExceededException as e:
        logger.warning(f"Rate limit exceeded for user {request.user_id}")
        raise HTTPException(status_code=429, detail=str(e))
    
    except ModelAPIException as e:
        logger.error(f"Model API error: {str(e)}")
        raise HTTPException(status_code=502, detail="Model service unavailable")
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/v1/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Streaming chat endpoint (placeholder for Phase 2+).
    
    Future implementation will support server-sent events or chunked responses
    to stream tokens as they are generated by the model.
    
    This enables real-time responses and better user experience for long outputs.
    """
    return {
        "status": "not_implemented",
        "message": "Streaming support will be added in Phase 2"
    }


@app.delete("/api/v1/session/{user_id}")
async def delete_session(user_id: str):
    """Delete a user session and clear conversation history."""
    deleted = session_store.delete_session(user_id)
    
    if deleted:
        # Also clear model client history
        if model_client:
            model_client.clear_history(user_id)
        
        logger.info(f"Session deleted for user {user_id}")
        return {"status": "success", "message": f"Session deleted for user {user_id}"}
    else:
        raise HTTPException(status_code=404, detail="Session not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=app_config.HOST,
        port=app_config.PORT,
        reload=True
    )
