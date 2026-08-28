"""Read example.com's public heading with a tightly bounded Browser Use agent."""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

from browser_use import Agent, Browser, ChatBrowserUse
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]


async def run() -> None:
    load_dotenv(ROOT / ".env")
    allowed = [d.strip() for d in os.getenv("BROWSER_USE_ALLOWED_DOMAINS", "example.com").split(",") if d.strip()]
    if "example.com" not in allowed:
        raise SystemExit("Safe demo requires example.com in BROWSER_USE_ALLOWED_DOMAINS")
    max_steps = min(max(int(os.getenv("BROWSER_USE_MAX_STEPS", "6")), 1), 10)

    browser = Browser(allowed_domains=allowed)
    agent = Agent(
        task=(
            "Open https://example.com/. Read only the page heading and page URL. "
            "Do not submit forms, download files, sign in, or navigate to another domain. "
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
        if data.get("url") not in {"https://example.com", "https://example.com/"}:
            raise RuntimeError("Agent returned an unexpected URL")
        print(json.dumps({"heading": str(data["heading"]), "url": data["url"]}))
    finally:
        await browser.stop()


if __name__ == "__main__":
    asyncio.run(run())
