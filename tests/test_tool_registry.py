"""Tests for tool registry schema validation."""

from pydantic import BaseModel, Field, ValidationError

from backend.tools.registry import ToolRegistry, ToolSpec


class EchoIn(BaseModel):
    text: str = Field(..., min_length=1)


class EchoOut(BaseModel):
    echoed: str


def test_registry_validates_input_and_output():
    registry = ToolRegistry()
    registry.register(
        ToolSpec(
            name="echo",
            description="Echo text",
            input_model=EchoIn,
            output_model=EchoOut,
            handler=lambda args: {"echoed": args.text},
        )
    )

    result = registry.execute("echo", {"text": "hello"})
    assert result["echoed"] == "hello"

    try:
        registry.execute("echo", {"text": ""})
        assert False, "Expected validation to fail for empty text"
    except ValidationError:
        assert True

