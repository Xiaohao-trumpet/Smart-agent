"""
LangGraph graph definition for the conversational AI system.
Phase 1: Single model node with extension points for future phases.
"""

from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from .node_calls import model_node


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


def create_chat_graph(model_client):
    """
    Create and compile the chat graph.
    
    Phase 1 flow:
    Entry → model_node → END
    
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
    
    # Add the model node
    # This node calls the model and updates the response in state
    workflow.add_node("model", lambda state: model_node(state, model_client))
    
    # Future nodes (placeholders for Phase 2+):
    # workflow.add_node("memory", memory_node)
    # workflow.add_node("tools", tool_node)
    # workflow.add_node("reflection", reflection_node)
    # workflow.add_node("planner", planner_node)
    
    # Set entry point
    workflow.set_entry_point("model")
    
    # Add edges
    # Phase 1: model → END
    workflow.add_edge("model", END)
    
    # Future edges (examples):
    # workflow.add_edge("memory", "planner")
    # workflow.add_edge("planner", "tools")
    # workflow.add_edge("tools", "model")
    # workflow.add_edge("model", "reflection")
    # workflow.add_conditional_edges("reflection", should_retry, {"retry": "model", "end": END})
    
    # Compile the graph
    app = workflow.compile()
    
    return app
