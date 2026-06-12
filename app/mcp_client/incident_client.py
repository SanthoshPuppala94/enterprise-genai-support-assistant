import asyncio
from typing import Any

from app.mcp_server.server import mcp


class IncidentMCPClient:
    """In-process MCP client adapter for the Incident RCA Agent.

    The production boundary is preserved: agents call MCP tools by name through
    this client instead of importing tool implementation functions directly.
    """

    def fetch_incident_details(self, incident_id: str) -> dict[str, Any]:
        return self._call_tool("fetch_incident_details", {"incident_id": incident_id})

    def fetch_batch_job_logs(self, batch_id: str) -> dict[str, Any]:
        return self._call_tool("fetch_batch_job_logs", {"batch_id": batch_id})

    def fetch_print_delivery_status(
        self,
        print_job_id: str | None = None,
        batch_id: str | None = None,
    ) -> dict[str, Any]:
        return self._call_tool(
            "fetch_print_delivery_status",
            {"print_job_id": print_job_id, "batch_id": batch_id},
        )

    def search_prior_resolutions(self, query: str) -> list[dict[str, Any]]:
        return self._call_tool("search_prior_resolutions", {"query": query})

    def search_incident_runbook(self, query: str) -> dict[str, str]:
        return self._call_tool("search_incident_runbook", {"query": query})

    def classify_resolution_path(self, incident_id: str) -> dict[str, Any]:
        return self._call_tool("classify_resolution_path", {"incident_id": incident_id})

    def correlate_incident_with_code_changes(
        self,
        incident_id: str,
        window_hours: int = 24,
    ) -> dict[str, Any]:
        return self._call_tool(
            "correlate_incident_with_code_changes",
            {"incident_id": incident_id, "window_hours": window_hours},
        )

    def draft_cr_summary(self, incident_id: str) -> dict[str, str]:
        return self._call_tool("draft_cr_summary", {"incident_id": incident_id})

    def draft_code_change_analysis(self, incident_id: str) -> dict[str, str]:
        return self._call_tool("draft_code_change_analysis", {"incident_id": incident_id})

    def _call_tool(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        return asyncio.run(self._call_tool_async(tool_name, arguments))

    async def _call_tool_async(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        _content, structured = await mcp.call_tool(tool_name, arguments)
        if isinstance(structured, dict) and "result" in structured:
            return structured["result"]
        return structured

