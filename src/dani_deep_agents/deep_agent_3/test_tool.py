"""Test if search_web tool works with create_react_agent."""
import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent
from search_web_tool import search_web

load_dotenv(os.path.join("..", "..", "..", ".env"), override=True)

model = init_chat_model(model="openai:gpt-4o-mini")

print("Creating agent with search_web tool...")
try:
    agent = create_react_agent(model, tools=[search_web])
    print("SUCCESS! Agent created.")
except Exception as e:
    print(f"FAILED: {e}")
