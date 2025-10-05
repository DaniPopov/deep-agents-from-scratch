"""State management for deep agents with TODO tracking and virtual file systems.

This module defines the extended agent state structure that supports:
- Task planning and progress tracking through TODO lists
- Context offloading through a virtual file system stored in state
- Efficient state merging with reducer functions
"""

from typing import Annotated, List
from typing_extensions import TypedDict, Literal, NotRequired

from langgraph.prebuilt.chat_agent_executor import AgentState

def reduce_list(left, right):
    """Safely combine two lists, handling cases where either or both inputs might be None.

    Args:
        left (list | None): The first list to combine, or None.
        right (list | None): The second list to combine, or None.

    Returns:
        list: A new list containing all elements from both input lists.
               If an input is None, it's treated as an empty list.
    """
    if not left:
        left = []
    if not right:
        right = []
    return left + right

def file_reducer(left, right):
    """Merge two file dictionaries, with right side taking precedence."""
    if not left:
        left = {}
    if not right:
        right = {}
    return {**left, **right}

class Todo(TypedDict):
    """A structured task item for tracking progress through complex workflows.

    Attributes:
        content: Short, specific description of the task
        status: Current state - pending, in_progress, or completed
    """
    content: str
    status: Literal["pending", "in_progress", "completed"]


class DeepAgentState(AgentState):
    """Graph State."""
    search_results: Annotated[list[str], reduce_list]
    todos: list[Todo]
    files: Annotated[NotRequired[dict[str, str]], file_reducer]
