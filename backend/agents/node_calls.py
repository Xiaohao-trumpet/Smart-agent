"""
Node implementations for the LangGraph workflow.
Each node is a function that takes state and returns updated state.
"""

from typing import Dict, Any
from ..models.universal_chat import UniversalChat


def model_node(state: Dict[str, Any], model_client: UniversalChat) -> Dict[str, Any]:
    """
    Model node: Calls the LLM and generates a response.
    
    Args:
        state: Current chat state containing user_id and user_message
        model_client: UniversalChat instance
    
    Returns:
        Updated state with response field populated
    """
    user_id = state["user_id"]
    user_message = state.get("model_input_message", state["user_message"])
    temperature = state.get("temperature")
    max_tokens = state.get("max_tokens")
    
    # Call the model
    response = model_client.chat(
        user_id=user_id,
        message=user_message,
        temperature=temperature,
        max_tokens=max_tokens,
        use_history=False,
    )
    
    # Update state
    return {
        **state,
        "response": response
    }


def memory_retrieve_node(
    state: Dict[str, Any],
    short_term_manager,
    memory_service,
    memory_enabled: bool,
    memory_top_k: int,
) -> Dict[str, Any]:
    """Retrieve short-term and long-term memories and inject into model input."""
    if not memory_enabled:
        return {
            **state,
            "model_input_message": state["user_message"],
            "retrieved_memories": [],
        }

    user_id = state["user_id"]
    user_message = state["user_message"]
    session = state.get("session")

    short_context_text = ""
    if short_term_manager is not None and session is not None:
        short_context = short_term_manager.build_context(session)
        short_context_text = short_term_manager.render_context(short_context)

    long_context_text = ""
    retrieved_memories = []
    if memory_service is not None:
        search_results = memory_service.search_memories(user_id=user_id, query=user_message, top_k=memory_top_k)
        retrieved_memories = [
            {
                "id": hit.memory.id,
                "text": hit.memory.text,
                "score": hit.score,
                "tags": hit.memory.tags,
                "metadata": hit.memory.metadata,
            }
            for hit in search_results
        ]
        if search_results:
            lines = [f"- ({hit.score:.3f}) {hit.memory.text}" for hit in search_results]
            long_context_text = "Relevant long-term memories:\n" + "\n".join(lines)

    context_blocks = []
    if short_context_text:
        context_blocks.append(short_context_text)
    if long_context_text:
        context_blocks.append(long_context_text)

    if context_blocks:
        model_input_message = (
            "Use the following memory context when relevant, but prioritize the latest user request.\n\n"
            + "\n\n".join(context_blocks)
            + "\n\nCurrent user message:\n"
            + user_message
        )
    else:
        model_input_message = user_message

    return {
        **state,
        "model_input_message": model_input_message,
        "retrieved_memories": retrieved_memories,
    }


def memory_write_node(
    state: Dict[str, Any],
    short_term_manager,
    memory_service,
    memory_enabled: bool,
    memory_write_enabled: bool,
) -> Dict[str, Any]:
    """Persist short-term turn and optionally extract/store long-term memory."""
    user_message = state.get("user_message", "")
    response = state.get("response", "")
    user_id = state.get("user_id")
    session = state.get("session")

    if short_term_manager is not None and session is not None and user_message and response:
        short_term_manager.append_turn(session, user_message=user_message, assistant_message=response)

    auto_memory = None
    if memory_enabled and memory_write_enabled and memory_service is not None and user_id and user_message:
        auto_memory = memory_service.extract_and_store(user_id=user_id, user_message=user_message)

    return {
        **state,
        "auto_memory": auto_memory.id if auto_memory else None,
    }


# Future node implementations (Phase 3+):

def memory_node(state: Dict[str, Any], memory_store) -> Dict[str, Any]:
    """
    Memory node: Retrieves relevant memories for the current conversation.
    
    Future implementation:
    - Query short-term memory (recent conversation context)
    - Query long-term memory (user preferences, past interactions)
    - Add retrieved memories to state
    
    Args:
        state: Current chat state
        memory_store: Memory storage backend
    
    Returns:
        Updated state with memories field
    """
    raise NotImplementedError("Memory node not implemented in Phase 1")


def tool_node(state: Dict[str, Any], tool_registry) -> Dict[str, Any]:
    """
    Tool node: Executes external tool calls.
    
    Future implementation:
    - Parse tool calls from model response
    - Execute tools (API calls, database queries, etc.)
    - Add tool results to state
    
    Args:
        state: Current chat state
        tool_registry: Registry of available tools
    
    Returns:
        Updated state with tool results
    """
    raise NotImplementedError("Tool node not implemented in Phase 1")


def reflection_node(state: Dict[str, Any], quality_checker) -> Dict[str, Any]:
    """
    Reflection node: Evaluates response quality and decides if retry is needed.
    
    Future implementation:
    - Check response quality (relevance, accuracy, completeness)
    - Assign reward score for RL optimization
    - Decide if response should be regenerated
    
    Args:
        state: Current chat state
        quality_checker: Quality evaluation component
    
    Returns:
        Updated state with reward_score and retry decision
    """
    raise NotImplementedError("Reflection node not implemented in Phase 1")


def planner_node(state: Dict[str, Any], planner) -> Dict[str, Any]:
    """
    Planner node: Generates multi-step reasoning plan.
    
    Future implementation:
    - Analyze user request complexity
    - Generate step-by-step plan
    - Determine which tools/resources are needed
    
    Args:
        state: Current chat state
        planner: Planning component
    
    Returns:
        Updated state with plan field
    """
    raise NotImplementedError("Planner node not implemented in Phase 1")
