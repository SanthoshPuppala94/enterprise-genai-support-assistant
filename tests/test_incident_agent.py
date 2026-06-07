from app.agents.incident_agent import IncidentRCAAgent


def test_incident_agent_returns_grounded_rca():
    state = IncidentRCAAgent().run({"question": "Why did INC-2026-1042 happen?"})
    assert state["agent_used"] == "incident_agent"
    assert "Incident RCA summary for INC-2026-1042" in state["answer"]
    assert "Previous engineer actions" in state["answer"]
    assert "Operational support action" in state["answer"]
    assert state["citations"]

