from app.graph.builder import build_graph
from app.memory.preference_store import PreferenceStore


def test_incident_rca_langgraph_nodes_populate_evidence(tmp_path):
    graph = build_graph(PreferenceStore(tmp_path / "prefs.db"))
    result = graph.invoke(
        {
            "question": "Was INC-2026-1042 related to a recent deployment or code change?",
            "user_id": "test-user",
            "history": [],
            "preferences": {},
            "agent_used": "",
            "answer": "",
            "citations": [],
            "sql_results": [],
        }
    )

    assert result["agent_used"] == "incident_agent"
    assert result["incident_id"] == "INC-2026-1042"
    assert result["incident"]["batch_id"] == "B-1002"
    assert result["batch_logs"]["signals"]
    assert result["print_status"]["print_job_id"] == "P-7781"
    assert result["prior_resolutions"]
    assert result["runbook"]["source"].endswith("incident_triage_runbook.md")
    assert result["code_correlation"]["failed_module"] == "file_handoff_worker"
    assert result["resolution_path"]["path"] == "Operational support action"
    assert "Recent code/deployment correlation" in result["answer"]

