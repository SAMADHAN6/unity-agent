"""
FastAPI backend — exposes the Unity agent as a REST API
"""

import os
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from agent.agent import create_unity_agent, run_agent
from knowledge.rag import build_knowledge_base, load_knowledge_base


load_dotenv()


# --- Lifespan: runs once at startup ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_knowledge_base()
    yield


app = FastAPI(
    title="Unity Game Dev AI Agent",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://samadhan6.github.io",
        "http://localhost",
        "http://127.0.0.1",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Global agent + per-session thread tracking
_agent = None
_sessions: dict[str, str] = {}   # session_id -> thread_id


def get_agent():
    global _agent
    if _agent is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=500,
                detail="GROQ_API_KEY is not set. Add it to your .env file."
            )
        _agent = create_unity_agent(api_key)
    return _agent


# --- Request / Response models ---

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"   # optional: pass a unique ID per browser tab

class ChatResponse(BaseModel):
    reply: str
    session_id: str


# --- Endpoints ---

@app.get("/")
def root():
    return {"status": "Unity Agent is running"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """Send a message to the Unity agent and get a response."""
    agent = get_agent()

    # Map session_id to a stable thread_id for memory continuity
    if request.session_id not in _sessions:
        _sessions[request.session_id] = str(uuid.uuid4())
    thread_id = _sessions[request.session_id]

    try:
        reply = run_agent(agent, request.message, thread_id=thread_id)
        return ChatResponse(reply=reply, session_id=request.session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/build-kb")
def build_kb():
    """Rebuild the knowledge base from .txt files in data/docs/."""
    try:
        build_knowledge_base()
        return {"status": "Knowledge base built successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/clear-history")
def clear_history(session_id: str = "default"):
    """Reset conversation memory for a session."""
    if session_id in _sessions:
        del _sessions[session_id]
    return {"status": f"History cleared for session '{session_id}'"}


# --- Run directly with: python main.py ---

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
