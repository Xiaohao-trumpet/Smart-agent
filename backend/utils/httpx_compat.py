"""Compatibility helpers for OpenAI SDK + newer httpx releases."""

from __future__ import annotations

import inspect
from typing import Any

import httpx


def patch_httpx_for_openai() -> None:
    """
    Patch httpx Client/AsyncClient constructors to accept legacy ``proxies``.

    OpenAI SDK versions pinned in this project may still pass ``proxies=...``
    into httpx constructors. Newer httpx versions removed that argument.
    This shim keeps local dev working when dependency trees pull newer httpx.
    """

    client_sig = inspect.signature(httpx.Client.__init__)
    async_sig = inspect.signature(httpx.AsyncClient.__init__)
    if "proxies" in client_sig.parameters and "proxies" in async_sig.parameters:
        return

    original_client_init = httpx.Client.__init__
    original_async_init = httpx.AsyncClient.__init__

    def _map_proxies(kwargs: dict[str, Any], proxies: Any) -> None:
        if proxies is None:
            return
        if "proxy" in kwargs:
            return

        if isinstance(proxies, str):
            kwargs["proxy"] = proxies
            return

        if isinstance(proxies, dict):
            kwargs["proxy"] = (
                proxies.get("https://")
                or proxies.get("http://")
                or proxies.get("all://")
                or proxies.get("all")
            )

    def patched_client_init(self, *args, proxies=None, **kwargs):
        _map_proxies(kwargs, proxies)
        return original_client_init(self, *args, **kwargs)

    def patched_async_init(self, *args, proxies=None, **kwargs):
        _map_proxies(kwargs, proxies)
        return original_async_init(self, *args, **kwargs)

    httpx.Client.__init__ = patched_client_init  # type: ignore[assignment]
    httpx.AsyncClient.__init__ = patched_async_init  # type: ignore[assignment]
