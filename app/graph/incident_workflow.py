import re

from app.agents.incident_agent import format_rca_answer
from app.graph.state import ChatState
from app.mcp_client.incident_client import IncidentMCPClient
from app.services.guardrails import apply_grounding_guardrails


class IncidentRCAWorkflow:
    def __init__(self, mcp_client: IncidentMCPClient | None = None):
        self.mcp_client = mcp_client or IncidentMCPClient()

    def intake(self, state: ChatState) -> ChatState:
        state["incident_id"] = _extract_incident_id(state["question"]) or "INC-2026-1042"
        state["agent_used"] = "incident_agent"
        return state

    def fetch_incident(self, state: ChatState) -> ChatState:
        state["incident"] = self.mcp_client.fetch_incident_details(state["incident_id"])
        return state

    def fetch_batch_logs(self, state: ChatState) -> ChatState:
        state["batch_logs"] = self.mcp_client.fetch_batch_job_logs(state["incident"]["batch_id"])
        return state

    def fetch_print_status(self, state: ChatState) -> ChatState:
        incident = state["incident"]
        state["print_status"] = self.mcp_client.fetch_print_delivery_status(
            print_job_id=incident.get("print_job_id"),
            batch_id=incident.get("batch_id"),
        )
        return state

    def search_prior_resolutions(self, state: ChatState) -> ChatState:
        state["prior_resolutions"] = self.mcp_client.search_prior_resolutions(
            " ".join(state["incident"].get("symptoms", []))
        )
        return state

    def search_runbook(self, state: ChatState) -> ChatState:
        state["runbook"] = self.mcp_client.search_incident_runbook(state["question"])
        return state

    def correlate_code_changes(self, state: ChatState) -> ChatState:
        state["code_correlation"] = self.mcp_client.correlate_incident_with_code_changes(state["incident_id"])
        return state

    def classify_resolution(self, state: ChatState) -> ChatState:
        state["resolution_path"] = self.mcp_client.classify_resolution_path(state["incident_id"])
        if state["resolution_path"]["cr_required"]:
            state["cr_summary"] = self.mcp_client.draft_cr_summary(state["incident_id"])
        else:
            state["cr_summary"] = None
        if state["code_correlation"]["confidence"] in {"medium", "high"}:
            state["code_change_analysis"] = self.mcp_client.draft_code_change_analysis(state["incident_id"])
        else:
            state["code_change_analysis"] = None
        return state

    def finalize(self, state: ChatState) -> ChatState:
        citations = [
            f"incident:{state['incident']['incident_id']}",
            state["batch_logs"]["source"],
            f"print_status:{state['print_status']['print_job_id']}",
            "prior_resolutions:engineer_actions.json",
            state["runbook"]["source"],
            "deployments:deployments.json",
            "repo_history:commits.json",
        ]
        answer = format_rca_answer(
            state["incident"],
            state["batch_logs"],
            state["print_status"],
            state["prior_resolutions"],
            state["resolution_path"],
            state["cr_summary"],
            state["code_correlation"],
            state["code_change_analysis"],
        )
        state["answer"] = apply_grounding_guardrails(answer, citations)
        state["citations"] = citations
        state["agent_used"] = "incident_agent"
        return state


def _extract_incident_id(text: str) -> str | None:
    match = re.search(r"\bINC-\d{4}-\d{4}\b", text.upper())
    return match.group(0) if match else None

