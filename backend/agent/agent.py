"""
Unity Game Dev AI Agent - Core Agent Logic
Uses Groq API (llama-3.3-70b-versatile) via LangChain 1.x create_agent.
"""

import os
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import MemorySaver
from .tools import get_tools

SYSTEM_PROMPT = """You are an expert Unity game development assistant with deep knowledge of:
- Unity Engine (2D, 3D, AR/VR)
- C# scripting and MonoBehaviour lifecycle
- Unity physics, animation, and UI systems
- Rendering pipelines: URP, HDRP, Built-in
- Performance optimization and profiling
- Unity DOTS / ECS architecture
- Asset management and addressables
- Unity editor scripting and custom tools

Always provide:
1. Clear, working C# code examples when relevant
2. References to official Unity docs when possible
3. Best practices and common pitfalls
4. Step-by-step explanations for complex topics

If you don't know something, say so honestly rather than guessing.
"""

DEFAULT_THREAD_ID = "unity-session"


def create_unity_agent(groq_api_key: str):
    """Create and return the Unity AI agent using Groq."""

    llm = ChatGroq(
        model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
        temperature=0.2,
        api_key=groq_api_key,
    )

    tools = get_tools()
    checkpointer = MemorySaver()

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
        checkpointer=checkpointer,
    )

    return agent


def run_agent(agent, message: str, thread_id: str = DEFAULT_THREAD_ID) -> str:
    """
    Send a message to the agent and return the response text.
    thread_id isolates conversation memory per session.
    """
    config = {"configurable": {"thread_id": thread_id}}
    result = agent.invoke(
        {"messages": [{"role": "user", "content": message}]},
        config=config
    )

    # Extract the last AI message
    messages = result.get("messages", [])
    for msg in reversed(messages):
        if hasattr(msg, "content") and getattr(msg, "type", None) == "ai":
            return msg.content
        if hasattr(msg, "role") and msg.role == "assistant":
            return msg.content

    if messages:
        last = messages[-1]
        return last.content if hasattr(last, "content") else str(last)

    return "No response generated."
