"""Short-term memory manager for session-level conversational context."""

from __future__ import annotations

from typing import Any, Dict, List


class ShortTermMemoryManager:
    """Manages sliding-window context and optional summary for a session."""

    def __init__(
        self,
        window_turns: int = 6,
        enable_summary: bool = True,
        summary_trigger_turns: int = 10,
        summary_max_chars: int = 800,
    ):
        self.window_turns = max(1, window_turns)
        self.enable_summary = enable_summary
        self.summary_trigger_turns = max(1, summary_trigger_turns)
        self.summary_max_chars = max(100, summary_max_chars)

    @staticmethod
    def _format_messages(messages: List[Dict[str, str]]) -> str:
        lines = []
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            lines.append(f"{role}: {content}")
        return "\n".join(lines)

    def _summarize(self, existing_summary: str, messages_to_summarize: List[Dict[str, str]]) -> str:
        """Simple local summarization fallback without extra model calls."""
        chunk = self._format_messages(messages_to_summarize)
        if existing_summary:
            combined = f"{existing_summary}\n{chunk}"
        else:
            combined = chunk

        if len(combined) <= self.summary_max_chars:
            return combined

        return combined[-self.summary_max_chars :]

    def append_turn(self, session: Any, user_message: str, assistant_message: str) -> None:
        """Append a full turn and compact history if summary is enabled."""
        session.add_message("user", user_message)
        session.add_message("assistant", assistant_message)

        if not self.enable_summary:
            return

        messages = session.get_messages()
        trigger_messages = self.summary_trigger_turns * 2
        keep_messages = self.window_turns * 2

        if len(messages) <= trigger_messages:
            return

        messages_for_summary = messages[:-keep_messages] if len(messages) > keep_messages else []
        if not messages_for_summary:
            return

        existing_summary = str(session.metadata.get("summary", ""))
        session.metadata["summary"] = self._summarize(existing_summary, messages_for_summary)

        # Keep only the recent sliding window in explicit conversation history.
        session.conversation_history = messages[-keep_messages:]

    def build_context(self, session: Any) -> Dict[str, Any]:
        """Build short-term context payload from a session."""
        summary = str(session.metadata.get("summary", ""))
        recent_messages = session.get_messages()[-(self.window_turns * 2) :]
        return {
            "summary": summary,
            "recent_messages": recent_messages,
        }

    def render_context(self, context: Dict[str, Any]) -> str:
        """Render short-term context into prompt text."""
        parts = []
        summary = context.get("summary", "")
        recent_messages = context.get("recent_messages", [])

        if summary:
            parts.append("Session summary:\n" + summary)

        if recent_messages:
            parts.append("Recent conversation:\n" + self._format_messages(recent_messages))

        return "\n\n".join(parts).strip()

