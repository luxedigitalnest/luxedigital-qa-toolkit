[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Here

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    throw "uv is required. Run .\bootstrap.ps1 first."
}

# stdio belongs to the MCP client; do not add logging or print environment values here.
uv run browser-use --mcp
