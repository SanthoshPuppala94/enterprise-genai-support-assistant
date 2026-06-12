from typing import Any

from mcp.server.fastmcp import FastMCP

from app.tools.sql_tools import execute_select as execute_select_tool


mcp = FastMCP(
    name="enterprise-support-db-mcp",
    instructions="Read-only database MCP server. SELECT-only SQL guardrails are enforced.",
)


@mcp.tool()
def execute_sql(query: str) -> list[dict[str, Any]]:
    """Execute a safe SELECT-only query against the mock SQLite database."""
    return execute_select_tool(query=query)


def run() -> None:
    mcp.run()


if __name__ == "__main__":
    run()

