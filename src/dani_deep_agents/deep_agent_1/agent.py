"""
Deep Agent with TODOs.

We will build a deep agent that will be used to answer hard question about use cases and tech specs
in computers, workstations, workspaces, etc. We will use a TODO list to keep track of the tasks we need to complete.
"""
import os
from dotenv import load_dotenv

from rich.console import Console

from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent

from utils import format_messages
from prompts import SYSTEM_PROMPT
from state import DeepAgentState
from search_web_tool import search_web
from todo_tools import write_todos, read_todos

if __name__ == "__main__":
    load_dotenv(os.path.join("..", "..", "..", ".env"), override=True)

    console = Console()
    model = init_chat_model(model="openai:gpt-4.1-mini")
    tools = [search_web, write_todos, read_todos] 

    agent = create_react_agent(
        model=model,
        tools=tools,
        prompt=SYSTEM_PROMPT,
        state_schema=DeepAgentState, 
    ).with_config({"recursion_limit": 20})

    # Initialize conversation state with DeepAgentState fields
    conversation_state = {"messages": [], "results": [], "todos": []}

    console.print("\n[bold cyan]🖥️  Deep Agent with TODOs[/bold cyan]")
    console.print("[yellow]Ask me anything! (Type 'exit' or 'quit' to end)[/yellow]\n")

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
            {
                "role": "user",
                "content": user_input
            }
        )

        # Store the number of messages before agent invocation
        num_messages_before = len(conversation_state["messages"])

        # Get agent response
        result = agent.invoke(conversation_state)

        # Update conversation state with all messages and results from result
        conversation_state = {
            "messages": result["messages"],
            "search_results": result.get("search_results", []),
            "todos": result.get("todos", [])
        }

        # Display all NEW messages from this exchange (everything after the previous count)
        console.print()  # Add spacing
        format_messages(result["messages"][num_messages_before:])

        # Display search results if any were added in this turn
        if result.get("results"):
            console.print("\n[bold yellow]🔍 Search Results Saved to State:[/bold yellow]")
            for idx, res in enumerate(result["results"], 1):
                console.print(f"  {idx}. {res}")
        
        # Display todos if any were added in this turn
        if result.get("todos"):
            console.print("\n[bold yellow]🔍 TODOs Saved to State:[/bold yellow]")
            for idx, todo in enumerate(result["todos"], 1):
                console.print(f"  {idx}. {todo}")

        console.print()  # Add spacing
