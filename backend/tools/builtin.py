"""Built-in tool implementations."""

from __future__ import annotations

from typing import Dict, Any

from .registry import ToolRegistry, ToolSpec
from .schemas import (
    KBSearchInput,
    KBSearchOutput,
    CreateTicketInput,
    CreateTicketOutput,
    GetTicketInput,
    GetTicketOutput,
    ListTicketsInput,
    ListTicketsOutput,
)
from .stores import FAQStore, TicketStore


def register_builtin_tools(registry: ToolRegistry, faq_store: FAQStore, ticket_store: TicketStore) -> None:
    """Register local-first built-in tools."""

    def kb_search_tool(args: KBSearchInput) -> Dict[str, Any]:
        hits = faq_store.search(query=args.query, top_k=args.top_k)
        return {"query": args.query, "hits": hits}

    def create_ticket_tool(args: CreateTicketInput) -> Dict[str, Any]:
        ticket = ticket_store.create_ticket(
            user_id=args.user_id,
            subject=args.subject,
            description=args.description,
            priority=args.priority,
            tags=args.tags,
        )
        return {
            "ticket_id": ticket.get("ticket_id", ""),
            "status": ticket.get("status", "open"),
            "user_id": ticket.get("user_id", args.user_id),
            "subject": ticket.get("subject", args.subject),
            "priority": ticket.get("priority", args.priority),
            "created_at": ticket.get("created_at", 0.0),
        }

    def get_ticket_tool(args: GetTicketInput) -> Dict[str, Any]:
        ticket = ticket_store.get_ticket(ticket_id=args.ticket_id)
        return {"found": ticket is not None, "ticket": ticket}

    def list_tickets_tool(args: ListTicketsInput) -> Dict[str, Any]:
        tickets = ticket_store.list_tickets(user_id=args.user_id, limit=args.limit)
        return {"user_id": args.user_id, "tickets": tickets}

    registry.register(
        ToolSpec(
            name="kb_search",
            description="Search local FAQ/knowledge base for policy or troubleshooting answers.",
            input_model=KBSearchInput,
            output_model=KBSearchOutput,
            handler=kb_search_tool,
        )
    )
    registry.register(
        ToolSpec(
            name="create_ticket",
            description="Create a support ticket and return ticket id.",
            input_model=CreateTicketInput,
            output_model=CreateTicketOutput,
            handler=create_ticket_tool,
        )
    )
    registry.register(
        ToolSpec(
            name="get_ticket",
            description="Get support ticket details by ticket id.",
            input_model=GetTicketInput,
            output_model=GetTicketOutput,
            handler=get_ticket_tool,
        )
    )
    registry.register(
        ToolSpec(
            name="list_tickets",
            description="List recent support tickets for a user.",
            input_model=ListTicketsInput,
            output_model=ListTicketsOutput,
            handler=list_tickets_tool,
        )
    )

