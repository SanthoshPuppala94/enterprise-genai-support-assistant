from app.agents.incident_agent import IncidentRCAAgent


def test_incident_agent_returns_grounded_rca():
    state = IncidentRCAAgent().run({"question": "Why did INC-2026-1042 happen?"})
    assert state["agent_used"] == "incident_agent"
    assert "Incident RCA summary for INC-2026-1042" in state["answer"]
    assert "Previous engineer actions" in state["answer"]
    assert "Operational support action" in state["answer"]
    assert "Recent code/deployment correlation" in state["answer"]
    assert "c0ffee1" in state["answer"]
    assert "must not edit code" in state["answer"]
    assert state["citations"]


def test_incident_agent_uses_mcp_client_boundary():
    class FakeIncidentMCPClient:
        def __init__(self):
            self.calls = []

        def fetch_incident_details(self, incident_id):
            self.calls.append(("fetch_incident_details", incident_id))
            return {
                "incident_id": incident_id,
                "business_impact": "Mock impact",
                "batch_id": "B-FAKE",
                "print_job_id": "P-FAKE",
                "symptoms": ["file acknowledgement timeout"],
            }

        def fetch_batch_job_logs(self, batch_id):
            self.calls.append(("fetch_batch_job_logs", batch_id))
            return {
                "source": "fake.log",
                "signals": ["STATUS=FAILED code=FILE_TRANSFER_TIMEOUT"],
            }

        def fetch_print_delivery_status(self, print_job_id=None, batch_id=None):
            self.calls.append(("fetch_print_delivery_status", print_job_id, batch_id))
            return {"print_job_id": "P-FAKE", "delivery_status": "Not delivered"}

        def search_prior_resolutions(self, query):
            self.calls.append(("search_prior_resolutions", query))
            return []

        def search_incident_runbook(self, query):
            self.calls.append(("search_incident_runbook", query))
            return {"source": "runbook.md", "text": "mock"}

        def classify_resolution_path(self, incident_id):
            self.calls.append(("classify_resolution_path", incident_id))
            return {"path": "Operational support action", "cr_required": False, "reason": "Mock reason"}

        def correlate_incident_with_code_changes(self, incident_id):
            self.calls.append(("correlate_incident_with_code_changes", incident_id))
            return {
                "failed_module": "file_handoff_worker",
                "confidence": "low",
                "recent_deployments": [],
                "related_commits": [],
                "guardrail": "must not edit code",
            }

        def draft_cr_summary(self, incident_id):
            self.calls.append(("draft_cr_summary", incident_id))
            return {}

        def draft_code_change_analysis(self, incident_id):
            self.calls.append(("draft_code_change_analysis", incident_id))
            return {}

    fake_client = FakeIncidentMCPClient()
    state = IncidentRCAAgent(fake_client).run({"question": "Why did INC-2026-9999 happen?"})
    called_tool_names = {call[0] for call in fake_client.calls}

    assert state["agent_used"] == "incident_agent"
    assert "fetch_incident_details" in called_tool_names
    assert "fetch_batch_job_logs" in called_tool_names
    assert "correlate_incident_with_code_changes" in called_tool_names

