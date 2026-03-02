"""Safe tool execution with allowlist, timeout, and rate limiting."""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from threading import Lock
from typing import Dict, List, Tuple

from .registry import ToolRegistry
from .schemas import ToolCall, ToolResult


class ToolExecutor:
    """Executes planned tool calls with guardrails."""

    def __init__(
        self,
        registry: ToolRegistry,
        allowlist: List[str],
        timeout_seconds: float = 3.0,
        rate_limit_per_minute: int = 30,
        max_calls_per_turn: int = 3,
    ):
        self.registry = registry
        self.allowlist = set(allowlist)
        self.timeout_seconds = max(0.1, timeout_seconds)
        self.rate_limit_per_minute = max(1, rate_limit_per_minute)
        self.max_calls_per_turn = max(1, max_calls_per_turn)
        self._rate_state: Dict[Tuple[str, str], List[float]] = {}
        self._lock = Lock()

    def _check_rate_limit(self, user_id: str, tool_name: str) -> None:
        now = time.time()
        key = (user_id, tool_name)
        with self._lock:
            recent = [ts for ts in self._rate_state.get(key, []) if now - ts <= 60.0]
            if len(recent) >= self.rate_limit_per_minute:
                raise RuntimeError(f"Tool rate limit exceeded for {tool_name}")
            recent.append(now)
            self._rate_state[key] = recent

    def _execute_one(self, user_id: str, call: ToolCall) -> ToolResult:
        start = time.time()
        if call.tool not in self.allowlist:
            return ToolResult(
                tool=call.tool,
                success=False,
                input=call.arguments,
                error=f"Tool not allowed: {call.tool}",
                latency_ms=(time.time() - start) * 1000.0,
            )

        try:
            self._check_rate_limit(user_id=user_id, tool_name=call.tool)
            with ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(self.registry.execute, call.tool, call.arguments)
                output = future.result(timeout=self.timeout_seconds)
            return ToolResult(
                tool=call.tool,
                success=True,
                input=call.arguments,
                output=output,
                latency_ms=(time.time() - start) * 1000.0,
            )
        except FuturesTimeoutError:
            return ToolResult(
                tool=call.tool,
                success=False,
                input=call.arguments,
                error=f"Tool call timed out after {self.timeout_seconds}s",
                latency_ms=(time.time() - start) * 1000.0,
            )
        except Exception as exc:
            return ToolResult(
                tool=call.tool,
                success=False,
                input=call.arguments,
                error=str(exc),
                latency_ms=(time.time() - start) * 1000.0,
            )

    def execute_plan(self, user_id: str, plan: List[ToolCall]) -> List[ToolResult]:
        results: List[ToolResult] = []
        for call in plan[: self.max_calls_per_turn]:
            results.append(self._execute_one(user_id=user_id, call=call))
        return results

