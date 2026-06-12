from app.mcp_servers.db_server import execute_sql
from app.mcp_servers.git_server import (
    classify_resolution_path,
    correlate_incident_with_code_changes,
    draft_code_change_analysis,
    fetch_commit_details,
    fetch_recent_deployments,
    search_repo_history,
)
from app.mcp_servers.incident_server import (
    draft_cr_summary,
    fetch_incident_details,
    search_prior_resolutions,
)
from app.mcp_servers.log_server import (
    analyze_logs,
    fetch_batch_job_logs,
    fetch_print_delivery_status,
)
from app.mcp_servers.runbook_server import (
    mock_incident_triage_runbook,
    mock_letter_templates,
    mock_policies,
    mock_runbooks,
    search_documents,
    search_incident_runbook,
)
from mcp.server.fastmcp import FastMCP


mcp = FastMCP(
    name="enterprise-genai-support-assistant-local-aggregate",
    instructions=(
        "Local aggregate MCP server for demos and MCP Inspector. Production uses separate "
        "domain MCP servers for incident, logs, database, git/deployment, and runbook/RAG."
    ),
)


for tool in (
    search_documents,
    execute_sql,
    analyze_logs,
    fetch_incident_details,
    fetch_batch_job_logs,
    fetch_print_delivery_status,
    search_prior_resolutions,
    search_incident_runbook,
    classify_resolution_path,
    draft_cr_summary,
    fetch_recent_deployments,
    search_repo_history,
    fetch_commit_details,
    correlate_incident_with_code_changes,
    draft_code_change_analysis,
):
    mcp.tool()(tool)

for uri, resource in (
    ("mock://policies/enterprise-support", mock_policies),
    ("mock://runbooks/file-transfer", mock_runbooks),
    ("mock://letter-templates/generation-sop", mock_letter_templates),
    ("mock://runbooks/incident-triage", mock_incident_triage_runbook),
):
    mcp.resource(uri)(resource)


def run() -> None:
    mcp.run()


if __name__ == "__main__":
    run()
