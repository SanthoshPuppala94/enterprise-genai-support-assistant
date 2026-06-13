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
    incident_id: str
    incident: dict[str, Any]
    batch_logs: dict[str, Any]
    print_status: dict[str, Any]
    prior_resolutions: list[dict[str, Any]]
    runbook: dict[str, str]
    resolution_path: dict[str, Any]
    code_correlation: dict[str, Any]
    cr_summary: dict[str, str] | None
    code_change_analysis: dict[str, str] | None
