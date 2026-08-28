"""Local, secret-safe readiness checks for the optional Browser Use layer."""

from __future__ import annotations

import importlib.metadata
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PROVIDER_KEYS = (
    "BROWSER_USE_API_KEY",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GOOGLE_API_KEY",
    "GEMINI_API_KEY",
    "GROQ_API_KEY",
    "AZURE_OPENAI_API_KEY",
)


def report(ok: bool, label: str, detail: str) -> bool:
    print(f"[{'PASS' if ok else 'FAIL'}] {label}: {detail}")
    return ok


def load_local_env(path: Path) -> None:
    """Load simple KEY=VALUE entries without requiring the optional environment."""
    if not path.is_file():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("'\""))


def browser_available() -> tuple[bool, str]:
    candidates = (
        Path(os.environ.get("LOCALAPPDATA", "")) / "ms-playwright",
        Path.home() / "AppData/Local/ms-playwright",
        Path.home() / ".cache/ms-playwright",
    )
    executables = ("msedge", "chrome", "chromium", "chromium-browser")
    if any(path.exists() and any(path.iterdir()) for path in candidates):
        return True, "a Playwright-managed browser directory exists"
    found = next((name for name in executables if shutil.which(name)), None)
    if found:
        return True, f"{found} is on PATH"
    return False, "no Chromium browser found; run 'uv run browser-use install chromium'"


def main() -> int:
    load_local_env(ROOT / ".env")
    results: list[bool] = []
    results.append(report(sys.version_info[:2] == (3, 12), "Python", sys.version.split()[0]))
    results.append(report(shutil.which("uv") is not None, "uv", shutil.which("uv") or "not found"))

    installed = importlib.util.find_spec("browser_use") is not None
    version = importlib.metadata.version("browser-use") if installed else "not installed"
    results.append(report(installed, "Browser Use import/version", version))

    browser_ok, browser_detail = browser_available()
    results.append(report(browser_ok, "Browser availability", browser_detail))

    cli = shutil.which("browser-use")
    mcp_ok = False
    mcp_detail = "browser-use executable not found"
    if cli:
        check = subprocess.run(
            [cli, "--help"], capture_output=True, text=True, timeout=20, check=False
        )
        help_text = f"{check.stdout}\n{check.stderr}".lower()
        mcp_ok = check.returncode == 0 and "mcp" in help_text
        mcp_detail = "CLI advertises MCP mode" if mcp_ok else "CLI help does not advertise --mcp"
    results.append(report(mcp_ok, "MCP startup readiness", mcp_detail))

    configured = [key for key in PROVIDER_KEYS if os.environ.get(key)]
    results.append(
        report(
            bool(configured),
            "Model credentials",
            "configured variable(s): " + ", ".join(configured)
            if configured
            else "none configured (values are never printed)",
        )
    )

    domains = [d.strip() for d in os.getenv("BROWSER_USE_ALLOWED_DOMAINS", "example.com").split(",") if d.strip()]
    results.append(report(bool(domains), "Allowed domains", f"{len(domains)} hostname(s) configured"))
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
