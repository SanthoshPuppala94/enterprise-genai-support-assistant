from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from app.config import ROOT_DIR
from app.tools.incident_tools import (
    classify_resolution_path as classify_resolution_path_tool,
    draft_cr_summary as draft_cr_summary_tool,
    fetch_batch_job_logs as fetch_batch_job_logs_tool,
    fetch_incident_details as fetch_incident_details_tool,
    fetch_print_delivery_status as fetch_print_delivery_status_tool,
    search_prior_resolutions as search_prior_resolutions_tool,
)
from app.tools.log_tools import analyze_logs as analyze_logs_tool
from app.tools.rag_tools import search_documents as search_documents_tool
from app.tools.sql_tools import execute_select as execute_select_tool


mcp = FastMCP(
    name="enterprise-genai-support-assistant",
    instructions=(
        "Mock production-style MCP server for enterprise correspondence support. "
        "All tools and resources use synthetic data only and contain no real client data."
    ),
)


def _read_mock_resource(relative_path: str) -> str:
    path = ROOT_DIR / relative_path
    return path.read_text(encoding="utf-8")


@mcp.tool()
def search_documents(query: str, k: int = 4) -> list[dict[str, str | float]]:
    """Search mock enterprise support policies, SOPs, runbooks, and letter documentation."""
    return search_documents_tool(query=query, k=k)


@mcp.tool()
def execute_sql(query: str) -> list[dict[str, Any]]:
    """Execute a safe SELECT-only query against the mock SQLite database."""
    return execute_select_tool(query=query)


@mcp.tool()
def analyze_logs() -> dict[str, object]:
    """Analyze synthetic enterprise correspondence application logs for known support signatures."""
    return analyze_logs_tool()


@mcp.tool()
def fetch_incident_details(incident_id: str) -> dict[str, Any]:
    """Fetch a synthetic incident ticket for correspondence batch triage."""
    return fetch_incident_details_tool(incident_id)


@mcp.tool()
def fetch_batch_job_logs(batch_id: str) -> dict[str, Any]:
    """Fetch synthetic cloud/container batch worker logs for a correspondence batch."""
    return fetch_batch_job_logs_tool(batch_id)


@mcp.tool()
def fetch_print_delivery_status(print_job_id: str | None = None, batch_id: str | None = None) -> dict[str, Any]:
    """Fetch synthetic PDF/print delivery status for a batch or print job."""
    return fetch_print_delivery_status_tool(print_job_id=print_job_id, batch_id=batch_id)


@mcp.tool()
def search_prior_resolutions(query: str) -> list[dict[str, Any]]:
    """Search previous synthetic incident resolutions and engineer actions."""
    return search_prior_resolutions_tool(query)


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
def draft_cr_summary(incident_id: str) -> dict[str, str]:
    """Draft a governed CR summary when RCA evidence indicates code/config change."""
    return draft_cr_summary_tool(incident_id)


@mcp.resource("mock://policies/enterprise-support")
def mock_policies() -> str:
    """Mock enterprise support policy documentation."""
    return _read_mock_resource("data/docs/enterprise_support_policy.md")


@mcp.resource("mock://runbooks/file-transfer")
def mock_runbooks() -> str:
    """Mock correspondence file transfer runbook."""
    return _read_mock_resource("data/docs/file_transfer_runbook.md")


@mcp.resource("mock://letter-templates/generation-sop")
def mock_letter_templates() -> str:
    """Mock letter generation SOP and template section guidance."""
    return _read_mock_resource("data/docs/letter_generation_sop.md")


@mcp.resource("mock://runbooks/incident-triage")
def mock_incident_triage_runbook() -> str:
    """Mock incident triage runbook for missing printed correspondence."""
    return _read_mock_resource("data/docs/incident_triage_runbook.md")


def run() -> None:
    mcp.run()


if __name__ == "__main__":
    run()
