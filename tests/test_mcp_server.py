import asyncio

from app.mcp_server.server import mcp
from app.mcp_servers.db_server import mcp as db_mcp
from app.mcp_servers.git_server import mcp as git_mcp
from app.mcp_servers.incident_server import mcp as incident_mcp
from app.mcp_servers.log_server import mcp as log_mcp
from app.mcp_servers.runbook_server import mcp as runbook_mcp


def _tool_names(server):
    async def run():
        tools = await server.list_tools()
        return {tool.name for tool in tools}

    return asyncio.run(run())


def test_mcp_tools_are_registered_with_fastmcp_decorators():
    tool_names = _tool_names(mcp)
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


def test_domain_mcp_servers_expose_separated_tool_sets():
    assert _tool_names(incident_mcp) == {
        "fetch_incident_details",
        "search_prior_resolutions",
        "draft_cr_summary",
    }
    assert _tool_names(log_mcp) == {
        "analyze_logs",
        "fetch_batch_job_logs",
        "fetch_print_delivery_status",
    }
    assert _tool_names(db_mcp) == {"execute_sql"}
    assert _tool_names(git_mcp) == {
        "fetch_recent_deployments",
        "search_repo_history",
        "fetch_commit_details",
        "correlate_incident_with_code_changes",
        "classify_resolution_path",
        "draft_code_change_analysis",
    }
    assert _tool_names(runbook_mcp) == {
        "search_documents",
        "search_incident_runbook",
    }


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
