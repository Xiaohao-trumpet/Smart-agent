"""Tool registry with input/output schema validation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Type

from pydantic import BaseModel


ToolHandler = Callable[[BaseModel], Dict[str, Any]]


@dataclass
class ToolSpec:
    name: str
    description: str
    input_model: Type[BaseModel]
    output_model: Type[BaseModel]
    handler: ToolHandler


class ToolRegistry:
    """Registry for safe, typed tool registration and execution."""

    def __init__(self):
        self._tools: Dict[str, ToolSpec] = {}

    def register(self, spec: ToolSpec) -> None:
        if spec.name in self._tools:
            raise ValueError(f"Tool already registered: {spec.name}")
        self._tools[spec.name] = spec

    def get(self, tool_name: str) -> ToolSpec:
        if tool_name not in self._tools:
            raise KeyError(f"Unknown tool: {tool_name}")
        return self._tools[tool_name]

    def list_tools(self) -> Dict[str, Dict[str, str]]:
        return {
            name: {
                "name": spec.name,
                "description": spec.description,
                "input_schema": spec.input_model.__name__,
                "output_schema": spec.output_model.__name__,
            }
            for name, spec in self._tools.items()
        }

    def validate_input(self, tool_name: str, arguments: Dict[str, Any]) -> BaseModel:
        spec = self.get(tool_name)
        return spec.input_model.model_validate(arguments)

    def execute(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        spec = self.get(tool_name)
        validated_input = spec.input_model.model_validate(arguments)
        raw_output = spec.handler(validated_input)
        validated_output = spec.output_model.model_validate(raw_output)
        return validated_output.model_dump()

