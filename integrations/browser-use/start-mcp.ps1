[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Here

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    throw "uv is required. Run .\bootstrap.ps1 first."
}

# Load non-empty local .env values into this process without printing them. This
# keeps credentials out of MCP client config and committed files.
$EnvFile = Join-Path $Here ".env"
if (Test-Path $EnvFile) {
    foreach ($RawLine in Get-Content $EnvFile) {
        $Line = $RawLine.Trim()
        if (-not $Line -or $Line.StartsWith("#") -or -not $Line.Contains("=")) {
            continue
        }

        $Parts = $Line -split "=", 2
        $Name = $Parts[0].Trim()
        $Value = $Parts[1].Trim()
        if ($Value.Length -ge 2) {
            if (($Value[0] -eq '"' -and $Value[-1] -eq '"') -or ($Value[0] -eq "'" -and $Value[-1] -eq "'")) {
                $Value = $Value.Substring(1, $Value.Length - 2)
            }
        }

        if ($Name -match '^[A-Za-z_][A-Za-z0-9_]*$' -and $Value) {
            [Environment]::SetEnvironmentVariable($Name, $Value, [EnvironmentVariableTarget]::Process)
        }
    }
}

# Project invariant: never weaken browser security to get around a site.
$env:BROWSER_USE_DISABLE_SECURITY = "false"

# stdout belongs to the MCP protocol; do not add logging or print environment values here.
uv run browser-use --mcp
