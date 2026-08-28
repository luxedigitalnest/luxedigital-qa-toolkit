# Optional Browser Use layer for LDN Sales Channel OS

This integration is deliberately isolated under `integrations/browser-use`. It does not change the QA package, its dependencies, its CLI, or its Playwright workflows. Browser Use is the agentic fallback—not a replacement for deterministic automation.

## Routing policy

Use the least powerful reliable route:

1. **Connector or direct API first.** Prefer supported, scoped, auditable interfaces.
2. **Playwright second.** Keep authenticated, known, deterministic browser workflows in the existing Playwright layer.
3. **Browser Use third.** Use it for unfamiliar or changing sites and bounded multi-step discovery where selectors and paths are not yet stable.
4. **Verify before writing.** Independently verify important extracted values, totals, identities, URLs, and intended mutations before updating Sales Channel OS. A browser agent's final response is not proof that an action succeeded.

## Windows 11 setup

Prerequisites are PowerShell and network access. From the repository root:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
cd .\integrations\browser-use
.\bootstrap.ps1
notepad .env
uv run python .\scripts\health_check.py
uv run python .\scripts\safe_demo.py
```

The bootstrap installs `uv` when absent, installs CPython 3.12, resolves the exact top-level pins into a local `uv.lock`, syncs that environment, installs Browser Use's Chromium, creates an ignored `.env` from `.env.example`, and runs the health check. Add one supported provider key to `.env`; never paste secrets into chat, logs, committed files, task text, or screenshots.

After the first successful connected setup, keep the generated `uv.lock` locally and use `uv sync --frozen` so transitive resolution cannot drift. To refresh dependencies intentionally, edit the exact pins in `pyproject.toml`, run `uv lock --upgrade`, review the diff, and rerun both checks.

## Local MCP

Run the stdio server directly:

```powershell
.\integrations\browser-use\start-mcp.ps1
```

For an MCP client, copy the `browser-use` entry from `mcp.example.json` into the client's local MCP configuration and replace the placeholder with the absolute repository path. The launcher intentionally emits no wrapper output on stdout because stdout carries MCP protocol messages. Keep `.env` local; MCP inherits the launcher process environment and Browser Use loads local configuration.

## Safety defaults

- Scope each job to the smallest `BROWSER_USE_ALLOWED_DOMAINS` list; the demo permits only `example.com`.
- Keep `BROWSER_USE_MAX_STEPS` low (default 6, hard demo cap 10). Stop and reassess rather than giving an agent an open-ended loop.
- Never disable Chromium security controls, certificate checks, or site protections.
- Browser Use tasks must be read-only by default. Do not allow purchases, payments, publication, deletion, account/security changes, permission changes, messages, or irreversible submissions.
- Do not place credentials, customer data, tokens, or other secrets in prompts. Do not log environment values. Use provider secret mechanisms and scoped test accounts.
- Require explicit human review immediately before any consequential write. Prefer handing a discovered stable workflow back to an API or Playwright implementation.
- Use a separate browser profile for agentic work. Do not point the demo or MCP server at the authenticated Playwright profile by default.

## Checks and troubleshooting

`scripts/health_check.py` checks Python 3.12, `uv`, the installed Browser Use distribution/version, a local Chromium installation, MCP CLI support, at least one model credential, and a nonempty domain allowlist. It reports environment-variable **names only**, never values.

The demo visits the IANA-reserved `example.com`, reads its heading and URL, validates the returned URL, prints a two-field JSON object, and closes the browser. It requires a configured model provider and network/browser access. It never logs in, submits, downloads, or mutates remote data.

If the MCP readiness check says the CLI does not advertise MCP, confirm the locked Browser Use release supports `browser-use --mcp` before changing the launcher. Do not silently substitute an unpinned global installation.
