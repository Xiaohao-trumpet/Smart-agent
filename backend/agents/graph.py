"""
LangGraph graph definition for the conversational AI system.
Phase 1: Single model node with extension points for future phases.
"""

from typing import TypedDict, Optional, Any, List
from langgraph.graph import StateGraph, END
from .node_calls import (
    memory_retrieve_node,
    planner_node,
    tool_execute_node,
    final_response_node,
    memory_write_node,
)


class ChatState(TypedDict):
    """
    State definition for the chat graph.
    
    Current fields (Phase 1):
    - user_id: User identifier
    - user_message: The user's input message
    - response: The assistant's response (None until generated)
    
    Future extension fields (Phase 2+):
    - memories: Retrieved short-term and long-term memories
    - tools_used: List of tools called during processing
    - reward_score: Quality/feedback score for RL optimization
    - plan: Multi-step reasoning plan
    - reflection: Self-evaluation results
    """
    user_id: str
    user_message: str
    response: Optional[str]
    temperature: Optional[float]
    max_tokens: Optional[int]
    session: Any
    model_input_message: Optional[str]
    short_context_text: Optional[str]
    retrieved_memories: List[dict]
    intent: Optional[str]
    tool_plan: List[dict]
    tool_results: List[dict]
    tool_errors: List[str]
    needs_tools: bool
    auto_memory: Optional[str]


def create_chat_graph(
    model_client,
    short_term_manager=None,
    memory_service=None,
    tool_planner=None,
    tool_executor=None,
    tool_registry=None,
    prompt_builder=None,
    prompt_scene: str = "default",
    memory_enabled: bool = True,
    memory_write_enabled: bool = True,
    memory_top_k: int = 3,
    tools_enabled: bool = True,
):
    """
    Create and compile the chat graph.
    
    Phase 2 flow:
    Entry → memory_retrieve → planner → tool_execute → final_response → memory_write → END
    
    Future phases will add:
    - memory_node: Read/write short-term and long-term memory
    - tool_node: Call external tools/APIs
    - reflection_node: Quality checking and self-evaluation
    - planner_node: Multi-step reasoning and plan generation
    
    Example future flow:
    Entry → memory_node → planner_node → tool_node → model_node → reflection_node → END
    
    Args:
        model_client: UniversalChat instance for model calls
    
    Returns:
        Compiled LangGraph application
    """
    # Create the state graph
    workflow = StateGraph(ChatState)
    
    # Memory retrieval before model call.
    workflow.add_node(
        "memory_retrieve",
        lambda state: memory_retrieve_node(
            state=state,
            short_term_manager=short_term_manager,
            memory_service=memory_service,
            memory_enabled=memory_enabled,
            memory_top_k=memory_top_k,
        ),
    )

    workflow.add_node(
        "planner",
        lambda state: planner_node(
            state=state,
            tool_planner=tool_planner,
            tools_enabled=tools_enabled,
        ),
    )

    workflow.add_node(
        "tool_execute",
        lambda state: tool_execute_node(
            state=state,
            tool_executor=tool_executor,
            tools_enabled=tools_enabled,
        ),
    )

    workflow.add_node(
        "final_response",
        lambda state: final_response_node(
            state=state,
            model_client=model_client,
            prompt_builder=prompt_builder,
            prompt_scene=prompt_scene,
            tool_registry=tool_registry,
        ),
    )

    # Memory writeback after model output.
    workflow.add_node(
        "memory_write",
        lambda state: memory_write_node(
            state=state,
            short_term_manager=short_term_manager,
            memory_service=memory_service,
            memory_enabled=memory_enabled,
            memory_write_enabled=memory_write_enabled,
        ),
    )
    
    # Future nodes (placeholders for Phase 2+):
    # workflow.add_node("memory", memory_node)
    # workflow.add_node("tools", tool_node)
    # workflow.add_node("reflection", reflection_node)
    # workflow.add_node("planner", planner_node)
    
    # Set entry point
    workflow.set_entry_point("memory_retrieve")
    
    # Add edges
    workflow.add_edge("memory_retrieve", "planner")
    workflow.add_edge("planner", "tool_execute")
    workflow.add_edge("tool_execute", "final_response")
    workflow.add_edge("final_response", "memory_write")
    workflow.add_edge("memory_write", END)
    
    # Future edges (examples):
    # workflow.add_edge("memory", "planner")
    # workflow.add_edge("planner", "tools")
    # workflow.add_edge("tools", "model")
    # workflow.add_edge("model", "reflection")
    # workflow.add_conditional_edges("reflection", should_retry, {"retry": "model", "end": END})
    
    # Compile the graph
    app = workflow.compile()
    
    return app
