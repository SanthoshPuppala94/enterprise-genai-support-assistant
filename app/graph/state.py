from typing import Any, TypedDict


class ChatState(TypedDict, total=False):
    question: str
    user_id: str
    history: list[dict[str, str]]
    preferences: dict[str, str]
    agent_used: str
    answer: str
    citations: list[str]
    sql_results: list[dict[str, Any]]

