"""Search web tool."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(env_path)

from langchain_core.tools import tool

@tool
def search_web(query: str) -> str:
    """Search the web for information.

    Args:
        query: The search query string

    Returns:
        Search results as a formatted string
    """
    # Import and instantiate inside the function to avoid Pydantic serialization issues
    from langchain_tavily import TavilySearch

    tavily = TavilySearch(max_results=5)
    results = tavily.invoke(query)

    # Format results
    if isinstance(results, list):
        formatted = []
        for idx, result in enumerate(results, 1):
            if isinstance(result, dict):
                title = result.get('title', 'N/A')
                url = result.get('url', 'N/A')
                content = result.get('content', 'N/A')
                formatted.append(f"{idx}. {title}\n   URL: {url}\n   Content: {content}\n")
            else:
                formatted.append(f"{idx}. {str(result)}\n")
        return "\n".join(formatted)
    else:
        return str(results)
