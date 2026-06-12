param(
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

$InspectorArgs = @(
    "@modelcontextprotocol/inspector",
    "--",
    $PythonCommand,
    "-m",
    "app.mcp_server"
)

Write-Host "Project root: $ProjectRoot"
Write-Host "MCP server command: $PythonCommand -m app.mcp_server"
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

