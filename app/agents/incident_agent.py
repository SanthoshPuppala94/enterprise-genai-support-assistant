import re

from app.graph.state import ChatState
from app.mcp_client.incident_client import IncidentMCPClient
from app.services.guardrails import add_mock_data_disclaimer, apply_grounding_guardrails


class IncidentRCAAgent:
    name = "incident_agent"

    def __init__(self, mcp_client: IncidentMCPClient | None = None):
        self.mcp_client = mcp_client or IncidentMCPClient()

    def run(self, state: ChatState) -> ChatState:
        incident_id = _extract_incident_id(state["question"]) or "INC-2026-1042"
        incident = self.mcp_client.fetch_incident_details(incident_id)
        batch_logs = self.mcp_client.fetch_batch_job_logs(incident["batch_id"])
        print_status = self.mcp_client.fetch_print_delivery_status(
            print_job_id=incident.get("print_job_id"),
            batch_id=incident.get("batch_id"),
        )
        prior_resolutions = self.mcp_client.search_prior_resolutions(" ".join(incident.get("symptoms", [])))
        runbook = self.mcp_client.search_incident_runbook(state["question"])
        resolution_path = self.mcp_client.classify_resolution_path(incident_id)
        code_correlation = self.mcp_client.correlate_incident_with_code_changes(incident_id)
        cr_summary = self.mcp_client.draft_cr_summary(incident_id) if resolution_path["cr_required"] else None
        code_change_analysis = (
            self.mcp_client.draft_code_change_analysis(incident_id)
            if code_correlation["confidence"] in {"medium", "high"}
            else None
        )
        citations = [
            f"incident:{incident['incident_id']}",
            batch_logs["source"],
            f"print_status:{print_status['print_job_id']}",
            "prior_resolutions:engineer_actions.json",
            runbook["source"],
            "deployments:deployments.json",
            "repo_history:commits.json",
        ]
        state["answer"] = apply_grounding_guardrails(
            _format_rca_answer(
                incident,
                batch_logs,
                print_status,
                prior_resolutions,
                resolution_path,
                cr_summary,
                code_correlation,
                code_change_analysis,
            ),
            citations,
        )
        state["citations"] = citations
        state["agent_used"] = self.name
        return state


def _format_rca_answer(
    incident,
    batch_logs,
    print_status,
    prior_resolutions,
    resolution_path,
    cr_summary,
    code_correlation,
    code_change_analysis,
) -> str:
    prior_lines = []
    for item in prior_resolutions[:2]:
        actions = "; ".join(item.get("actions_taken", [])[:3])
        prior_lines.append(
            f"- {item['incident_id']} ({item['resolution_type']}): {actions}. Notes: {item['notes']}"
        )
    prior_text = "\n".join(prior_lines) if prior_lines else "- No similar prior resolution found in mock data."
    failed_signals = "\n".join(f"- {line}" for line in batch_logs.get("signals", []))
    cr_text = ""
    if cr_summary:
        cr_text = (
            "\n\nCR draft guidance:\n"
            f"- {cr_summary['title']}\n"
            f"- {cr_summary['summary']}\n"
            f"- Governance: {cr_summary['governance']}"
        )
    deployment_lines = []
    for deployment in code_correlation.get("recent_deployments", []):
        deployment_lines.append(
            f"- {deployment['deployment_id']} deployed at {deployment['deployed_at']} "
            f"({deployment['hours_before_incident']} hours before incident): {deployment['summary']}"
        )
    commit_lines = []
    for commit in code_correlation.get("related_commits", [])[:2]:
        commit_lines.append(
            f"- {commit['commit_id']} committed at {commit['committed_at']} "
            f"module={commit['module']} linked_cr={commit['linked_cr']}: {commit['summary']}"
        )
    code_text = (
        "\n\nRecent code/deployment correlation:\n"
        f"- Failed module inferred from logs: {code_correlation['failed_module']}\n"
        f"- Correlation confidence: {code_correlation['confidence']}\n"
        f"- Related deployments:\n{chr(10).join(deployment_lines) if deployment_lines else '- None found in window'}\n"
        f"- Related commits:\n{chr(10).join(commit_lines) if commit_lines else '- None found'}\n"
        f"- Guardrail: {code_correlation['guardrail']}"
    )
    if code_change_analysis:
        code_text += (
            "\n\nCode-change analysis draft:\n"
            f"- {code_change_analysis['title']}\n"
            f"- {code_change_analysis['analysis']}\n"
            f"- Guardrail: {code_change_analysis['guardrail']}"
        )
    answer = (
        f"Incident RCA summary for {incident['incident_id']}\n\n"
        f"Business impact: {incident['business_impact']}\n"
        f"Affected batch: {incident['batch_id']} on cloud-managed container batch workers\n"
        f"Print job: {incident['print_job_id']} status={print_status['delivery_status']}\n\n"
        "Confirmed log signals:\n"
        f"{failed_signals}\n\n"
        "Previous engineer actions to review before taking action:\n"
        f"{prior_text}\n\n"
        "Probable failure area:\n"
        f"- {resolution_path['reason']}\n\n"
        "Recommended path:\n"
        f"- {resolution_path['path']}\n"
        f"- CR required: {'Yes' if resolution_path['cr_required'] else 'No'}\n"
        "- Human approval is required before rerun, reprocess, CR creation, or production changes."
        f"{code_text}"
        f"{cr_text}"
    )
    return add_mock_data_disclaimer(answer)


def _extract_incident_id(text: str) -> str | None:
    match = re.search(r"\bINC-\d{4}-\d{4}\b", text.upper())
    return match.group(0) if match else None

