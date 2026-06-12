param(
    [ValidateSet("aggregate", "incident", "log", "db", "git", "runbook")]
    [string]$Server = "aggregate",
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

if (Test-Path $VenvPython) {
    $PythonCommand = $VenvPython
} else {
    $PythonCommand = "python"
}

$ServerModules = @{
    aggregate = "app.mcp_server"
    incident = "app.mcp_servers.incident_server"
    log = "app.mcp_servers.log_server"
    db = "app.mcp_servers.db_server"
    git = "app.mcp_servers.git_server"
    runbook = "app.mcp_servers.runbook_server"
}

$ServerModule = $ServerModules[$Server]

$InspectorArgs = @(
    "@modelcontextprotocol/inspector",
    "--",
    $PythonCommand,
    "-m",
    $ServerModule
)

Write-Host "Project root: $ProjectRoot"
Write-Host "MCP server profile: $Server"
Write-Host "MCP server command: $PythonCommand -m $ServerModule"
Write-Host "Inspector UI: http://127.0.0.1:6274"
Write-Host "Inspector proxy: http://127.0.0.1:6277"

if ($DryRun) {
    Write-Host "Dry run only. Command:"
    Write-Host "npx $($InspectorArgs -join ' ')"
    exit 0
}

Push-Location $ProjectRoot
try {
    & npx @InspectorArgs
} finally {
    Pop-Location
}
