# Optional Browser Use layer for LDN Sales Channel OS

This integration is deliberately isolated under `integrations/browser-use`. It does not replace the QA package or deterministic Playwright workflows. Browser Use is the agentic fallback for changing or unfamiliar browser work.

## Routing policy

Use the least powerful reliable route:

1. **Connector or direct API first.** Prefer scoped, auditable interfaces.
2. **Playwright second.** Keep authenticated, known, deterministic browser workflows in the existing Playwright layer.
3. **Browser Use third.** Use it for unfamiliar/changing sites, bounded multi-step discovery, recovery, and structured extraction.
4. **Verify before writing.** Independently verify important values, identities, URLs, and mutations before updating Sales Channel OS. A browser agent's final response is not evidence by itself.

Only record Browser Use as the execution method when a Browser Use MCP/tool actually executed the job. If it is not connected to the current ChatGPT/project runtime, use Playwright or report the exact blocker; never pretend Browser Use ran.

## Current pinned runtime

The optional environment pins Browser Use CLI `0.13.8` and Python `3.12.*`. Keep the exact pin until an intentional dependency review.

## Windows 11 setup

From the repository root:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
cd .\integrations\browser-use
.\bootstrap.ps1
notepad .env
uv run python .\scripts\health_check.py
uv run python .\scripts\safe_demo.py
```

The bootstrap installs `uv` when absent, installs CPython 3.12, syncs the pinned environment, runs `browser-use install`, creates an ignored `.env` when needed, runs Browser Use's first-party `--doctor` check, and runs our structural health check. Bootstrap deliberately does **not** require a model key so initial setup can finish safely. Afterward, add exactly one supported provider key to `.env`, then run the full health check and safe demo.

Optional coding-agent helper:

```powershell
uv run browser-use skill install
```

Do not install the skill automatically on machines where you do not want it to modify coding-agent configuration.

After a successful connected setup, keep the generated `uv.lock` locally and use `uv sync --frozen` so transitive resolution cannot drift. To refresh dependencies intentionally, update the exact pin, run `uv lock --upgrade`, review the diff, and rerun both checks.

## Local MCP

Run the stdio server:

```powershell
.\integrations\browser-use\start-mcp.ps1
```

For an MCP client, copy the `browser-use` entry from `mcp.example.json` into the client's local configuration and replace the placeholder path with the absolute repository path.

`start-mcp.ps1` loads non-empty values from the local ignored `.env` into the MCP process without printing them. It also forces `BROWSER_USE_DISABLE_SECURITY=false`. Never put provider/API keys in `mcp.example.json`, project instructions, committed files, task text, screenshots, or chat.

The direct upstream local MCP command remains:

```powershell
uvx --from 'browser-use[cli]' browser-use --mcp
```

Use the repository launcher for LDN work because it keeps the pinned environment and safety defaults together.

## Cloud MCP

Browser Use Cloud MCP can be configured with:

- endpoint: `https://api.browser-use.com/mcp`
- authentication header: `x-browser-use-api-key`

Keep that key in the MCP client's secret/environment mechanism. Do not paste it into the Sales OS database or project sources.

## Safety defaults

- Scope every job to the smallest practical explicit hostname list. Do not use an unrestricted `*` allowlist.
- Treat domain allowlists as defense in depth, not as the only security boundary. Keep tasks narrow and reject non-HTTP navigation schemes in sensitive workflows.
- Keep `BROWSER_USE_MAX_STEPS` between 1 and 10 for Sales OS agentic jobs unless a reviewed adapter explicitly requires more.
- Keep `BROWSER_USE_DISABLE_SECURITY=false`. Never weaken certificate, origin, browser, or site security just to bypass a blocker.
- Browser Use jobs are read-only by default. Do not allow purchases, payments, publication, deletion, credential/security changes, messages, permission changes, or irreversible submissions without explicit owner authorization and final verification.
- Do not place passwords, API keys, customer PII, payout data, tax data, or other secrets in prompts or logs.
- Use a separate Browser Use profile by default. Reuse an authenticated profile only when intentionally configured for that exact workflow and required by the job.
- Avoid duplicate tabs, downloads, registrations, accounts, or submissions.
- Give every job a narrow objective, allowed domains, stop condition, and step budget.
- If Browser Use discovers a stable path, move the repeatable write operation back to a direct API or deterministic Playwright adapter when practical.

## Verification before Sales OS updates

For meaningful state changes, use this sequence:

`inspect live state → select connector / Playwright / Browser Use → execute → independently verify → update Sales OS → report result + exact blocker`

Examples of evidence suitable for a Sales OS status update include an authoritative API response, a fresh seller-dashboard state, a public listing URL plus matching admin state, or deterministic Playwright confirmation. A queued check, an agent narration, or an old screenshot is not enough.

## Checks and troubleshooting

`scripts/health_check.py` verifies:

- Python 3.12 and `uv`
- Browser Use import/version and CLI availability
- CLI `--mcp` support
- Browser Use `--doctor` result on a full check
- at least one configured model credential on a full check
- explicit hostname allowlist configuration
- a 1–10 step budget
- browser security remains enabled

It reports provider variable **names only**, never values. Use `--skip-credentials` only during initial bootstrap.

`scripts/safe_demo.py` visits only `https://example.com`, blocks IP-address navigation, keeps browser security enabled, reads the heading and URL, validates the exact two-field JSON result, and closes the browser. It does not sign in, submit forms, download, publish, or mutate remote state.

If MCP readiness fails, run:

```powershell
uv run browser-use --doctor
uv run browser-use --help
```

Confirm the pinned Browser Use release still exposes `--mcp` before changing the launcher. Do not silently substitute an unpinned global installation.
