"""
Prompt factory for loading and managing system prompts.
Externalizes prompts from business logic for easier maintenance and customization.
"""

import os
from typing import Dict, Optional
from pathlib import Path


class PromptFactory:
    """Factory for loading and formatting system prompts."""
    
    def __init__(self, prompts_dir: Optional[str] = None):
        """
        Initialize the prompt factory.
        
        Args:
            prompts_dir: Directory containing prompt files. 
                        Defaults to the directory containing this file.
        """
        if prompts_dir is None:
            prompts_dir = Path(__file__).parent
        self.prompts_dir = Path(prompts_dir)
        self._cache: Dict[str, str] = {}
    
    def get_system_prompt(self, scene: str = "default") -> str:
        """
        Load a system prompt for the given scene.
        
        Args:
            scene: The scene identifier (e.g., "default", "it_helpdesk")
        
        Returns:
            The system prompt text
        
        Raises:
            FileNotFoundError: If the prompt file doesn't exist
        """
        # Check cache first
        if scene in self._cache:
            return self._cache[scene]
        
        # Map scene to filename
        filename_map = {
            "default": "system.txt",
            "it_helpdesk": "it_helpdesk.txt"
        }
        
        filename = filename_map.get(scene, f"{scene}.txt")
        prompt_path = self.prompts_dir / filename
        
        if not prompt_path.exists():
            raise FileNotFoundError(
                f"Prompt file not found: {prompt_path}. "
                f"Available scenes: {list(filename_map.keys())}"
            )
        
        # Load and cache the prompt
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt = f.read().strip()
        
        self._cache[scene] = prompt
        return prompt
    
    def format_prompt(self, scene: str, context: Optional[Dict] = None) -> str:
        """
        Load and format a system prompt with dynamic context.
        
        Args:
            scene: The scene identifier
            context: Optional dictionary of context variables to inject
        
        Returns:
            The formatted system prompt
        
        Future enhancement: Support template variables like {user_name}, {preferences}, etc.
        """
        prompt = self.get_system_prompt(scene)
        
        if context:
            # Future: Implement template variable substitution
            # For now, just return the base prompt
            # Example future implementation:
            # prompt = prompt.format(**context)
            pass
        
        return prompt
    
    def clear_cache(self) -> None:
        """Clear the prompt cache. Useful for development/testing."""
        self._cache.clear()


# Global prompt factory instance
_prompt_factory: Optional[PromptFactory] = None


def get_prompt_factory() -> PromptFactory:
    """Get or create the global prompt factory instance."""
    global _prompt_factory
    if _prompt_factory is None:
        _prompt_factory = PromptFactory()
    return _prompt_factory
