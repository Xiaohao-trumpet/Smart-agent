"""
Model abstraction layer.
Provides a unified interface to different OpenAI-compatible backends.
"""

from .universal_chat import UniversalChat

__all__ = ["UniversalChat"]
