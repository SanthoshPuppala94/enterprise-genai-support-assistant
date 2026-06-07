from app.graph.state import ChatState
from app.services.guardrails import add_mock_data_disclaimer, apply_grounding_guardrails
from app.tools.incident_tools import (
    classify_resolution_path,
    draft_cr_summary,
    extract_incident_id,
    fetch_batch_job_logs,
    fetch_incident_details,
    fetch_print_delivery_status,
    search_incident_runbook,
    search_prior_resolutions,
)


class IncidentRCAAgent:
    name = "incident_agent"

    def run(self, state: ChatState) -> ChatState:
        incident_id = extract_incident_id(state["question"]) or "INC-2026-1042"
        incident = fetch_incident_details(incident_id)
        batch_logs = fetch_batch_job_logs(incident["batch_id"])
        print_status = fetch_print_delivery_status(
            print_job_id=incident.get("print_job_id"),
            batch_id=incident.get("batch_id"),
        )
        prior_resolutions = search_prior_resolutions(" ".join(incident.get("symptoms", [])))
        runbook = search_incident_runbook(state["question"])
        resolution_path = classify_resolution_path(incident, batch_logs, print_status, prior_resolutions)
        cr_summary = draft_cr_summary(incident_id) if resolution_path["cr_required"] else None
        citations = [
            f"incident:{incident['incident_id']}",
            batch_logs["source"],
            f"print_status:{print_status['print_job_id']}",
            "prior_resolutions:engineer_actions.json",
            runbook["source"],
        ]
        state["answer"] = apply_grounding_guardrails(
            _format_rca_answer(incident, batch_logs, print_status, prior_resolutions, resolution_path, cr_summary),
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
    answer = (
        f"Incident RCA summary for {incident['incident_id']}\n\n"
        f"Business impact: {incident['business_impact']}\n"
        f"Affected batch: {incident['batch_id']} on enterprise VM batch servers\n"
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
        f"{cr_text}"
    )
    return add_mock_data_disclaimer(answer)

