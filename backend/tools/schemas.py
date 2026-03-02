"""Typed schemas for tool planning and execution."""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    """A single planned tool call."""

    tool: str = Field(..., min_length=1)
    arguments: Dict[str, Any] = Field(default_factory=dict)
    reason: Optional[str] = None


class ToolResult(BaseModel):
    """Result of one tool call."""

    tool: str
    success: bool
    input: Dict[str, Any] = Field(default_factory=dict)
    output: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    latency_ms: float = 0.0


class PlannerOutput(BaseModel):
    """Planner decision for the current turn."""

    intent: str = "general_chat"
    needs_tools: bool = False
    plan: List[ToolCall] = Field(default_factory=list)


class KBSearchInput(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=3, ge=1, le=10)


class KBSearchOutput(BaseModel):
    query: str
    hits: List[Dict[str, Any]] = Field(default_factory=list)


class CreateTicketInput(BaseModel):
    user_id: str = Field(..., min_length=1)
    subject: str = Field(..., min_length=1, max_length=120)
    description: str = Field(..., min_length=1, max_length=2000)
    priority: Literal["low", "medium", "high", "urgent"] = "medium"
    tags: List[str] = Field(default_factory=list)


class CreateTicketOutput(BaseModel):
    ticket_id: str
    status: str
    user_id: str
    subject: str
    priority: str
    created_at: float


class GetTicketInput(BaseModel):
    ticket_id: str = Field(..., min_length=1)


class GetTicketOutput(BaseModel):
    found: bool
    ticket: Optional[Dict[str, Any]] = None


class ListTicketsInput(BaseModel):
    user_id: str = Field(..., min_length=1)
    limit: int = Field(default=10, ge=1, le=50)


class ListTicketsOutput(BaseModel):
    user_id: str
    tickets: List[Dict[str, Any]] = Field(default_factory=list)

