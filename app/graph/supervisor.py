from app.graph.state import ChatState


SQL_TERMS = ("sql", "query", "database", "batch", "job", "letter_status", "customer", "select")
RAG_TERMS = ("policy", "sop", "runbook", "documentation", "retention", "approval", "file transfer")
LOG_TERMS = ("log", "error", "failed", "timeout", "exception", "troubleshoot", "transfer")
LETTER_TERMS = ("letter", "printed", "template", "paragraph", "section", "explain output")
INCIDENT_TERMS = (
    "inc",
    "incident",
    "rca",
    "root cause",
    "missing printed",
    "not received",
    "business user",
    "previous engineer",
    "prior resolution",
    "cr required",
    "change request",
)


def route_question(state: ChatState) -> str:
    question = state["question"].lower()
    preferred = state.get("preferences", {}).get("preferred_agent")
    if preferred in {"sql_agent", "rag_agent", "log_agent", "letter_agent", "incident_agent"}:
        return preferred
    if any(term in question for term in INCIDENT_TERMS):
        return "incident_agent"
    if any(term in question for term in SQL_TERMS):
        return "sql_agent"
    if any(term in question for term in LOG_TERMS):
        return "log_agent"
    if any(term in question for term in LETTER_TERMS):
        return "letter_agent"
    if any(term in question for term in RAG_TERMS):
        return "rag_agent"
    return "rag_agent"
