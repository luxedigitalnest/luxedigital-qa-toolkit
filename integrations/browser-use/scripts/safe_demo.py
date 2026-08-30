"""Read example.com's public heading with a tightly bounded Browser Use agent."""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

from browser_use import Agent, Browser, ChatBrowserUse
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
DISALLOWED_SCHEMES = ("file:", "data:", "javascript:", "about:", "chrome:")


def security_enabled() -> bool:
    value = os.getenv("BROWSER_USE_DISABLE_SECURITY", "false").strip().lower()
    return value not in {"1", "true", "yes", "on"}


async def run() -> None:
    load_dotenv(ROOT / ".env")
    if not security_enabled():
        raise SystemExit("Refusing to run while BROWSER_USE_DISABLE_SECURITY is enabled")

    allowed = [
        d.strip()
        for d in os.getenv("BROWSER_USE_ALLOWED_DOMAINS", "example.com").split(",")
        if d.strip()
    ]
    if "example.com" not in allowed:
        raise SystemExit("Safe demo requires example.com in BROWSER_USE_ALLOWED_DOMAINS")
    if any(d == "*" or "://" in d or d.lower().startswith(DISALLOWED_SCHEMES) for d in allowed):
        raise SystemExit("Safe demo accepts explicit hostnames only; wildcard/scheme entries are refused")

    try:
        configured_steps = int(os.getenv("BROWSER_USE_MAX_STEPS", "6"))
    except ValueError as exc:
        raise SystemExit("BROWSER_USE_MAX_STEPS must be an integer") from exc
    max_steps = min(max(configured_steps, 1), 10)

    browser = Browser(
        allowed_domains=allowed,
        block_ip_addresses=True,
        disable_security=False,
        keep_alive=False,
    )
    agent = Agent(
        task=(
            "Open https://example.com/ using HTTPS only. Read only the page heading and page URL. "
            "Do not submit forms, download files, sign in, execute javascript/data/file URLs, "
            "open another origin, or mutate browser/account state. "
            "Return JSON with exactly the string fields heading and url."
        ),
        llm=ChatBrowserUse(),
        browser=browser,
        use_vision=False,
    )
    try:
        history = await agent.run(max_steps=max_steps)
        final = history.final_result()
        if not final:
            raise RuntimeError("Agent returned no final result")
        data = json.loads(final)
        if set(data) != {"heading", "url"}:
            raise RuntimeError("Agent returned unexpected fields")
        if not isinstance(data["heading"], str) or not isinstance(data["url"], str):
            raise RuntimeError("Agent returned non-string values")
        if data["url"] not in {"https://example.com", "https://example.com/"}:
            raise RuntimeError("Agent returned an unexpected URL")
        print(json.dumps({"heading": data["heading"], "url": data["url"]}))
    finally:
        await browser.stop()


if __name__ == "__main__":
    asyncio.run(run())
