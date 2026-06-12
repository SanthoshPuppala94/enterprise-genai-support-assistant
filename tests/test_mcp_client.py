from app.mcp_client.incident_client import IncidentMCPClient


def test_incident_mcp_client_calls_fastmcp_tools():
    client = IncidentMCPClient()
    incident = client.fetch_incident_details("INC-2026-1042")
    logs = client.fetch_batch_job_logs(incident["batch_id"])
    runbook = client.search_incident_runbook("missing printed correspondence")

    assert incident["batch_id"] == "B-1002"
    assert logs["signals"]
    assert "incident_triage_runbook.md" in runbook["source"]


def test_incident_mcp_client_routes_to_domain_servers():
    client = IncidentMCPClient()
    assert client.tool_server_map["fetch_incident_details"].name == "enterprise-support-incident-mcp"
    assert client.tool_server_map["fetch_batch_job_logs"].name == "enterprise-support-log-mcp"
    assert client.tool_server_map["search_incident_runbook"].name == "enterprise-support-runbook-mcp"
    assert client.tool_server_map["correlate_incident_with_code_changes"].name == "enterprise-support-git-mcp"
