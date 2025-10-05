"""
Basic React Agent.

We will build a basic React agent that will be used to answer hard question about use cases and tech specs
in computers, workstations, workspaces, etc.
"""
import os
from dotenv import load_dotenv

from rich.console import Console

from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent

from utils import format_messages
from prompts import SYSTEM_PROMPT
from state import DeepAgentState
from search_web_tool import search_web_with_state

if __name__ == "__main__":
    load_dotenv(os.path.join("..", "..", "..", ".env"), override=True)

    console = Console()
    model = init_chat_model(model="openai:gpt-4o-mini")
    tools = [search_web_with_state]  
    agent = create_react_agent(
        model=model,
        tools=tools,
        prompt=SYSTEM_PROMPT,
        state_schema=DeepAgentState,  # Use TechSpecsState to track search results
    ).with_config({"recursion_limit": 20})

    # Initialize conversation state with TechSpecsState fields
    conversation_state = {"messages": [], "results": []}

    console.print("\n[bold cyan]🖥️  Tech Specs Expert Agent[/bold cyan]")
    console.print("[yellow]Ask me anything about computer hardware! (Type 'exit' or 'quit' to end)[/yellow]\n")

    while True:
        # Get user input
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[yellow]Goodbye![/yellow]")
            break

        # Check for exit commands
        if user_input.lower() in ["exit", "quit", "bye"]:
            console.print("\n[yellow]Goodbye![/yellow]")
            break

        # Skip empty input
        if not user_input:
            continue

        # Add user message to conversation
        conversation_state["messages"].append(
            {"role": "user", "content": user_input}
        )

        # Store the number of messages before agent invocation
        num_messages_before = len(conversation_state["messages"])

        # Get agent response
        result = agent.invoke(conversation_state)

        # Update conversation state with all messages and results from result
        conversation_state = {
            "messages": result["messages"],
            "results": result.get("results", [])
        }

        # Display all NEW messages from this exchange (everything after the previous count)
        console.print()  # Add spacing
        format_messages(result["messages"][num_messages_before:])

        # Display search results if any were added in this turn
        if result.get("results"):
            console.print("\n[bold yellow]🔍 Search Results Saved to State:[/bold yellow]")
            for idx, res in enumerate(result["results"], 1):
                console.print(f"  {idx}. {res}")

        console.print()  # Add spacing
