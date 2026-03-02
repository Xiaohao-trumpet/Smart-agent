"""
Prompt management module.
Provides externalized prompts and prompt factory for loading them.
"""

from .prompt_factory import get_prompt_factory, PromptFactory

__all__ = ["get_prompt_factory", "PromptFactory"]
