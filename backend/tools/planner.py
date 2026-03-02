"""Rule-based intent router and tool planner."""

from __future__ import annotations

import re
from typing import List

from .schemas import PlannerOutput, ToolCall


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _priority_from_text(text: str) -> str:
    if any(word in text for word in ["urgent", "asap", "critical", "immediately", "紧急", "马上"]):
        return "urgent"
    if any(word in text for word in ["cannot", "can't", "not working", "down", "失败", "故障"]):
        return "high"
    if any(word in text for word in ["minor", "later"]):
        return "low"
    return "medium"


class ToolPlanner:
    """Deterministic planner for tool routing."""

    def __init__(self, tools_enabled: bool = True, max_calls_per_turn: int = 3):
        self.tools_enabled = tools_enabled
        self.max_calls_per_turn = max(1, max_calls_per_turn)

    def plan(self, user_id: str, user_message: str) -> PlannerOutput:
        text = _normalize(user_message)
        if not self.tools_enabled:
            return PlannerOutput(intent="general_chat", needs_tools=False, plan=[])

        plan: List[ToolCall] = []
        intent = "general_chat"

        if any(k in text for k in ["refund", "policy", "return policy", "退款", "退货"]):
            intent = "kb_question"
            plan.append(
                ToolCall(
                    tool="kb_search",
                    arguments={"query": user_message, "top_k": 3},
                    reason="User asks for policy/FAQ information.",
                )
            )

        ticket_id_match = re.search(r"\b(t[0-9a-f]{6,12})\b", text, flags=re.IGNORECASE)
        if any(k in text for k in ["ticket status", "check ticket", "ticket", "工单状态", "查询工单"]) and ticket_id_match:
            intent = "ticket_lookup"
            plan.append(
                ToolCall(
                    tool="get_ticket",
                    arguments={"ticket_id": ticket_id_match.group(1).upper()},
                    reason="User asks for a specific ticket status.",
                )
            )
        elif any(k in text for k in ["my tickets", "list tickets", "show tickets", "我的工单"]):
            intent = "ticket_list"
            plan.append(
                ToolCall(
                    tool="list_tickets",
                    arguments={"user_id": user_id, "limit": 5},
                    reason="User asks for their recent tickets.",
                )
            )
        elif any(
            k in text
            for k in [
                "open a ticket",
                "create ticket",
                "support ticket",
                "raise a ticket",
                "internet not working",
                "network down",
                "创建工单",
                "报障",
                "网络故障",
            ]
        ):
            intent = "ticket_create"
            subject = user_message.strip().split(".")[0][:100] or "Support request"
            plan.append(
                ToolCall(
                    tool="create_ticket",
                    arguments={
                        "user_id": user_id,
                        "subject": subject,
                        "description": user_message.strip(),
                        "priority": _priority_from_text(text),
                        "tags": ["auto", "chat"],
                    },
                    reason="User requests support and likely needs a new ticket.",
                )
            )

        if len(plan) > self.max_calls_per_turn:
            plan = plan[: self.max_calls_per_turn]

        return PlannerOutput(
            intent=intent,
            needs_tools=len(plan) > 0,
            plan=plan,
        )

