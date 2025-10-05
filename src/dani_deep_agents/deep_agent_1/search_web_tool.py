"""Search web tool."""
import json
from typing import Annotated
from langchain_core.tools import InjectedToolCallId, tool
from langgraph.types import Command
from langchain_tavily import TavilySearch
from langchain_core.messages import ToolMessage

@tool(parse_docstring=True)
def search_web(
    query: str,
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Search the web for information on a specific topic and save results to state.

    This tool performs web searches and returns relevant results
    for the given query. Use this when you need to gather information from
    the internet about any topic.

    Args:
        query: The search query string. Be specific and clear about what
               information you're looking for.
        tool_call_id: Injected tool call identifier for message tracking

    Returns:
        Search results from search engine.

    Example:
        search_web("What is the best GPU for gaming in 2024?")
    """
    # Initialize Tavily Search Tool (done here to ensure env vars are loaded)
    tavily_search_tool = TavilySearch(max_results=5, topic="general")

    # Perform search using Tavily
    search_input = {"query": query}

    search_results = tavily_search_tool.invoke(search_input)

    # Handle different return types from Tavily
    if isinstance(search_results, dict) and 'results' in search_results:
        # Tavily returns a dict with 'results' key containing list of result dicts
        results_state = []
        for idx, result in enumerate(search_results['results'], 1):
            url = result.get('url', 'N/A')
            title = result.get('title', 'N/A')
            content = result.get('content', 'N/A')
            formatted = f"{idx}. Title: {title}\n   URL: {url}\n   Content: {content}"
            results_state.append(formatted)
        tool_message_content = json.dumps(search_results, indent=2)
    elif isinstance(search_results, str):
        # If it's a string, store it directly
        results_state = [f"Search query: {query}", f"Results: {search_results}"]
        tool_message_content = search_results
    elif isinstance(search_results, list):
        # If it's a list, format each result
        results_state = []
        for idx, result in enumerate(search_results, 1):
            if isinstance(result, dict):
                url = result.get('url', 'N/A')
                title = result.get('title', 'N/A')
                content = result.get('content', 'N/A')
                formatted = f"{idx}. Title: {title}\n   URL: {url}\n   Content: {content}"
                results_state.append(formatted)
            else:
                results_state.append(f"{idx}. {str(result)}")
        tool_message_content = json.dumps(search_results, indent=2)
    else:
        # Otherwise convert to string
        results_state = [f"Search query: {query}", str(search_results)]
        tool_message_content = str(search_results)

    return Command(
        update={
            "search_results": results_state,
            "messages": [ToolMessage(tool_message_content, tool_call_id=tool_call_id)],
        }
    )
