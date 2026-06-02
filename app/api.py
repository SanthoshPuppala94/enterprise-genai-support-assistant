from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.config import get_settings
from app.graph.builder import build_graph
from app.graph.state import ChatState
from app.memory.preference_store import PreferenceStore


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1)
    user_id: str = "demo-user"


class ChatResponse(BaseModel):
    answer: str
    agent_used: str
    citations: list[str] = []


settings = get_settings()
preference_store = PreferenceStore(settings.db_path)
graph = build_graph(preference_store)

app = FastAPI(title=settings.app_name, version="0.1.0")


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    preferences = preference_store.get_preferences(request.user_id)
    state: ChatState = {
        "question": request.question,
        "user_id": request.user_id,
        "history": [],
        "preferences": preferences,
        "agent_used": "",
        "answer": "",
        "citations": [],
        "sql_results": [],
    }
    result = graph.invoke(state)
    return ChatResponse(
        answer=result["answer"],
        agent_used=result["agent_used"],
        citations=result.get("citations", []),
    )

