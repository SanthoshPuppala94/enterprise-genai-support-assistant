from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from app.config import ROOT_DIR
from app.tools.log_tools import analyze_logs as analyze_logs_tool
from app.tools.rag_tools import search_documents as search_documents_tool
from app.tools.sql_tools import execute_select as execute_select_tool


mcp = FastMCP(
    name="enterprise-lws-genai-assistant",
    instructions=(
        "Mock production-style MCP server for enterprise LWS/LCD letter support. "
        "All tools and resources use synthetic data only and contain no real client data."
    ),
)


def _read_mock_resource(relative_path: str) -> str:
    path = ROOT_DIR / relative_path
    return path.read_text(encoding="utf-8")


@mcp.tool()
def search_documents(query: str, k: int = 4) -> list[dict[str, str | float]]:
    """Search mock LWS/LCD policies, SOPs, runbooks, and letter documentation."""
    return search_documents_tool(query=query, k=k)


@mcp.tool()
def execute_sql(query: str) -> list[dict[str, Any]]:
    """Execute a safe SELECT-only query against the mock SQLite database."""
    return execute_select_tool(query=query)


@mcp.tool()
def analyze_logs() -> dict[str, object]:
    """Analyze synthetic LWS/LCD application logs for known support signatures."""
    return analyze_logs_tool()


@mcp.resource("mock://policies/lws")
def mock_policies() -> str:
    """Mock LWS policy documentation."""
    return _read_mock_resource("data/docs/lws_policy.md")


@mcp.resource("mock://runbooks/lcd-file-transfer")
def mock_runbooks() -> str:
    """Mock LCD file transfer runbook."""
    return _read_mock_resource("data/docs/lcd_file_transfer_runbook.md")


@mcp.resource("mock://letter-templates/generation-sop")
def mock_letter_templates() -> str:
    """Mock letter generation SOP and template section guidance."""
    return _read_mock_resource("data/docs/letter_generation_sop.md")


def run() -> None:
    mcp.run()


if __name__ == "__main__":
    run()
