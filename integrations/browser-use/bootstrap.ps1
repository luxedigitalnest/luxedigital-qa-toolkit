[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Here

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "Installing uv with the official standalone installer..."
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    $env:Path = "$env:USERPROFILE\.local\bin;$env:USERPROFILE\.cargo\bin;$env:Path"
}

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    throw "uv was installed but is not on PATH. Open a new PowerShell window and rerun this script."
}

uv python install 3.12
uv sync
uv run browser-use install

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created integrations\browser-use\.env. Add one model-provider API key locally; do not commit it."
}

# First-party diagnostics plus our secret-safe structural checks. Credentials are
# intentionally optional during bootstrap so a fresh install can complete before
# the owner edits .env.
uv run browser-use --doctor
uv run python scripts\health_check.py --skip-credentials

Write-Host "Browser Use runtime setup complete."
Write-Host "Next: add one provider key to .env, then run:"
Write-Host "  uv run python scripts\health_check.py"
Write-Host "  uv run python scripts\safe_demo.py"
Write-Host "Optional coding-agent skill: uv run browser-use skill install"
