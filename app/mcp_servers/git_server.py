from typing import Any

from mcp.server.fastmcp import FastMCP

from app.tools.incident_tools import (
    classify_resolution_path as classify_resolution_path_tool,
    correlate_incident_with_code_changes as correlate_incident_with_code_changes_tool,
    draft_code_change_analysis as draft_code_change_analysis_tool,
    fetch_batch_job_logs as fetch_batch_job_logs_tool,
    fetch_commit_details as fetch_commit_details_tool,
    fetch_incident_details as fetch_incident_details_tool,
    fetch_print_delivery_status as fetch_print_delivery_status_tool,
    fetch_recent_deployments as fetch_recent_deployments_tool,
    search_prior_resolutions as search_prior_resolutions_tool,
    search_repo_history as search_repo_history_tool,
)


mcp = FastMCP(
    name="enterprise-support-git-mcp",
    instructions=(
        "Read-only Git/deployment correlation MCP server. It must never edit, commit, push, "
        "merge, or deploy code."
    ),
)


@mcp.tool()
def fetch_recent_deployments(before_timestamp: str, hours: int = 24) -> list[dict[str, Any]]:
    """Read-only lookup of recent synthetic deployment records before an incident."""
    return fetch_recent_deployments_tool(before_timestamp=before_timestamp, hours=hours)


@mcp.tool()
def search_repo_history(query: str) -> list[dict[str, Any]]:
    """Read-only search of synthetic commit history by module, error code, or keyword."""
    return search_repo_history_tool(query)


@mcp.tool()
def fetch_commit_details(commit_id: str) -> dict[str, Any]:
    """Read-only lookup of synthetic commit metadata."""
    return fetch_commit_details_tool(commit_id)


@mcp.tool()
def correlate_incident_with_code_changes(incident_id: str, window_hours: int = 24) -> dict[str, Any]:
    """Correlate incident evidence with recent deployments and commit history without modifying code."""
    incident = fetch_incident_details_tool(incident_id)
    logs = fetch_batch_job_logs_tool(incident["batch_id"])
    return correlate_incident_with_code_changes_tool(incident, logs, window_hours=window_hours)


@mcp.tool()
def classify_resolution_path(incident_id: str) -> dict[str, Any]:
    """Classify whether an incident appears operational or CR/change-request related."""
    incident = fetch_incident_details_tool(incident_id)
    logs = fetch_batch_job_logs_tool(incident["batch_id"])
    status = fetch_print_delivery_status_tool(
        print_job_id=incident.get("print_job_id"),
        batch_id=incident.get("batch_id"),
    )
    prior = search_prior_resolutions_tool(" ".join(incident.get("symptoms", [])))
    return classify_resolution_path_tool(incident, logs, status, prior)


@mcp.tool()
def draft_code_change_analysis(incident_id: str) -> dict[str, str]:
    """Draft a code-change analysis for CR review; never edits, commits, pushes, or deploys code."""
    return draft_code_change_analysis_tool(incident_id)


def run() -> None:
    mcp.run()


if __name__ == "__main__":
    run()

