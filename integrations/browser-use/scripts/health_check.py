"""Local, secret-safe readiness checks for the optional Browser Use layer."""

from __future__ import annotations

import argparse
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
    """Load simple KEY=VALUE entries without printing or overwriting secrets."""
    if not path.is_file():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        if key and value:
            os.environ.setdefault(key, value)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--skip-credentials",
        action="store_true",
        help="Run structural setup checks without requiring a model-provider key.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    load_local_env(ROOT / ".env")
    results: list[bool] = []

    results.append(report(sys.version_info[:2] == (3, 12), "Python", sys.version.split()[0]))
    results.append(report(shutil.which("uv") is not None, "uv", shutil.which("uv") or "not found"))

    installed = importlib.util.find_spec("browser_use") is not None
    version = importlib.metadata.version("browser-use") if installed else "not installed"
    results.append(report(installed, "Browser Use import/version", version))

    cli = shutil.which("browser-use")
    results.append(report(cli is not None, "Browser Use CLI", cli or "not found"))

    if cli:
        help_check = subprocess.run(
            [cli, "--help"], capture_output=True, text=True, timeout=20, check=False
        )
        help_text = f"{help_check.stdout}\n{help_check.stderr}".lower()
        mcp_ok = help_check.returncode == 0 and "--mcp" in help_text
        results.append(
            report(
                mcp_ok,
                "MCP startup readiness",
                "CLI advertises --mcp" if mcp_ok else "CLI does not advertise --mcp",
            )
        )

        doctor = subprocess.run(
            [cli, "--doctor"], capture_output=True, text=True, timeout=60, check=False
        )
        doctor_ok = doctor.returncode == 0
        report(
            doctor_ok,
            "Browser Use doctor",
            "first-party diagnostics passed"
            if doctor_ok
            else "first-party diagnostics reported an issue; run 'browser-use --doctor' locally for details",
        )
        if not args.skip_credentials:
            results.append(doctor_ok)

    configured = [key for key in PROVIDER_KEYS if os.environ.get(key)]
    if args.skip_credentials:
        report(
            bool(configured),
            "Model credentials",
            "configured variable(s): " + ", ".join(configured)
            if configured
            else "not configured yet (allowed during bootstrap; values are never printed)",
        )
    else:
        results.append(
            report(
                bool(configured),
                "Model credentials",
                "configured variable(s): " + ", ".join(configured)
                if configured
                else "none configured (values are never printed)",
            )
        )

    domains = [
        d.strip()
        for d in os.getenv("BROWSER_USE_ALLOWED_DOMAINS", "example.com").split(",")
        if d.strip()
    ]
    domains_ok = bool(domains) and all(
        d != "*" and "://" not in d and not d.lower().startswith(("file:", "data:", "javascript:", "about:", "chrome:"))
        for d in domains
    )
    results.append(
        report(
            domains_ok,
            "Allowed domains",
            f"{len(domains)} hostname(s) configured; no unrestricted wildcard/scheme entries"
            if domains_ok
            else "use explicit hostnames only; '*' and URL/scheme entries are rejected",
        )
    )

    try:
        max_steps = int(os.getenv("BROWSER_USE_MAX_STEPS", "6"))
        steps_ok = 1 <= max_steps <= 10
    except ValueError:
        max_steps = -1
        steps_ok = False
    results.append(
        report(
            steps_ok,
            "Step budget",
            str(max_steps) if steps_ok else "must be an integer from 1 through 10",
        )
    )

    disable_security = os.getenv("BROWSER_USE_DISABLE_SECURITY", "false").strip().lower()
    security_ok = disable_security not in {"1", "true", "yes", "on"}
    results.append(
        report(
            security_ok,
            "Browser security",
            "enabled" if security_ok else "BROWSER_USE_DISABLE_SECURITY must remain false",
        )
    )

    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
