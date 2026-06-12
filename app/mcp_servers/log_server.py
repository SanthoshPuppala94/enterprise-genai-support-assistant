from typing import Any

from mcp.server.fastmcp import FastMCP

from app.tools.incident_tools import (
    fetch_batch_job_logs as fetch_batch_job_logs_tool,
    fetch_print_delivery_status as fetch_print_delivery_status_tool,
)
from app.tools.log_tools import analyze_logs as analyze_logs_tool


mcp = FastMCP(
    name="enterprise-support-log-mcp",
    instructions="Read-only log and print delivery MCP server for correspondence batch triage.",
)


@mcp.tool()
def analyze_logs() -> dict[str, object]:
    """Analyze synthetic enterprise correspondence application logs for known support signatures."""
    return analyze_logs_tool()


@mcp.tool()
def fetch_batch_job_logs(batch_id: str) -> dict[str, Any]:
    """Fetch synthetic cloud/container batch worker logs for a correspondence batch."""
    return fetch_batch_job_logs_tool(batch_id)


@mcp.tool()
def fetch_print_delivery_status(print_job_id: str | None = None, batch_id: str | None = None) -> dict[str, Any]:
    """Fetch synthetic PDF/print delivery status for a batch or print job."""
    return fetch_print_delivery_status_tool(print_job_id=print_job_id, batch_id=batch_id)


def run() -> None:
    mcp.run()


if __name__ == "__main__":
    run()

