from pathlib import Path

from mcp.server.fastmcp import FastMCP

from app.config import ROOT_DIR
from app.tools.incident_tools import search_incident_runbook as search_incident_runbook_tool
from app.tools.rag_tools import search_documents as search_documents_tool


mcp = FastMCP(
    name="enterprise-support-runbook-mcp",
    instructions="RAG and runbook MCP server for policies, SOPs, and incident guidance.",
)


def _read_mock_resource(relative_path: str) -> str:
    path = ROOT_DIR / relative_path
    return path.read_text(encoding="utf-8")


@mcp.tool()
def search_documents(query: str, k: int = 4) -> list[dict[str, str | float]]:
    """Search mock enterprise support policies, SOPs, runbooks, and letter documentation."""
    return search_documents_tool(query=query, k=k)


@mcp.tool()
def search_incident_runbook(query: str) -> dict[str, str]:
    """Read the synthetic incident triage runbook for grounded RCA guidance."""
    return search_incident_runbook_tool(query)


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

