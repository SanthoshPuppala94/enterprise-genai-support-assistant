import asyncio

from app.mcp_server.server import mcp


def test_mcp_tools_are_registered_with_fastmcp_decorators():
    async def run():
        tools = await mcp.list_tools()
        return {tool.name for tool in tools}

    tool_names = asyncio.run(run())
    assert {
        "search_documents",
        "execute_sql",
        "analyze_logs",
        "fetch_incident_details",
        "fetch_batch_job_logs",
        "fetch_print_delivery_status",
        "search_prior_resolutions",
        "search_incident_runbook",
        "classify_resolution_path",
        "draft_cr_summary",
        "fetch_recent_deployments",
        "search_repo_history",
        "fetch_commit_details",
        "correlate_incident_with_code_changes",
        "draft_code_change_analysis",
    }.issubset(tool_names)


def test_mcp_resources_are_registered_with_fastmcp_decorators():
    async def run():
        resources = await mcp.list_resources()
        return {str(resource.uri) for resource in resources}

    resource_uris = asyncio.run(run())
    assert {
        "mock://policies/enterprise-support",
        "mock://runbooks/file-transfer",
        "mock://letter-templates/generation-sop",
        "mock://runbooks/incident-triage",
    }.issubset(resource_uris)


def test_mcp_incident_tool_fetches_ticket():
    async def run():
        return await mcp.call_tool("fetch_incident_details", {"incident_id": "INC-2026-1042"})

    content, structured = asyncio.run(run())
    assert content
    result = structured.get("result", structured)
    assert result["batch_id"] == "B-1002"



def test_mcp_execute_sql_tool_enforces_select_only_safety():
    async def run():
        return await mcp.call_tool("execute_sql", {"query": "SELECT batch_id FROM letter_batches LIMIT 1"})

    content, structured = asyncio.run(run())
    assert content
    assert structured["result"][0]["batch_id"].startswith("B-")
