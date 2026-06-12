from typing import Any

from mcp.server.fastmcp import FastMCP

from app.tools.incident_tools import (
    draft_cr_summary as draft_cr_summary_tool,
    fetch_incident_details as fetch_incident_details_tool,
    search_prior_resolutions as search_prior_resolutions_tool,
)


mcp = FastMCP(
    name="enterprise-support-incident-mcp",
    instructions="Incident-record MCP server for ticket details, prior resolutions, and CR summaries.",
)


@mcp.tool()
def fetch_incident_details(incident_id: str) -> dict[str, Any]:
    """Fetch a synthetic incident ticket for correspondence batch triage."""
    return fetch_incident_details_tool(incident_id)


@mcp.tool()
def search_prior_resolutions(query: str) -> list[dict[str, Any]]:
    """Search previous synthetic incident resolutions and engineer actions."""
    return search_prior_resolutions_tool(query)


@mcp.tool()
def draft_cr_summary(incident_id: str) -> dict[str, str]:
    """Draft a governed CR summary when RCA evidence indicates code/config change."""
    return draft_cr_summary_tool(incident_id)


def run() -> None:
    mcp.run()


if __name__ == "__main__":
    run()

