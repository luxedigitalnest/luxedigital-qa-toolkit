"""Read example.com's public heading with a tightly bounded Browser Use agent."""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

from browser_use import (
    Agent,
    Browser,
    ChatAnthropic,
    ChatAzureOpenAI,
    ChatBrowserUse,
    ChatGoogle,
    ChatGroq,
    ChatOpenAI,
)
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
DISALLOWED_SCHEMES = ("file:", "data:", "javascript:", "about:", "chrome:")


def security_enabled() -> bool:
    value = os.getenv("BROWSER_USE_DISABLE_SECURITY", "false").strip().lower()
    return value not in {"1", "true", "yes", "on"}


def build_llm():
    """Choose one explicitly configured native Browser Use model provider."""
    model = os.getenv("BROWSER_USE_LLM_MODEL", "").strip()
    if os.getenv("BROWSER_USE_API_KEY"):
        return ChatBrowserUse(model=model) if model else ChatBrowserUse()
    if os.getenv("OPENAI_API_KEY"):
        return ChatOpenAI(model=model or "gpt-5")
    if os.getenv("ANTHROPIC_API_KEY"):
        return ChatAnthropic(model=model or "claude-sonnet-4-6")
    if os.getenv("GOOGLE_API_KEY"):
        return ChatGoogle(model=model or "gemini-2.5-flash")
    if os.getenv("GROQ_API_KEY"):
        return ChatGroq(model=model or "meta-llama/llama-4-maverick-17b-128e-instruct")
    if os.getenv("AZURE_OPENAI_API_KEY") and os.getenv("AZURE_OPENAI_ENDPOINT"):
        return ChatAzureOpenAI(model=model or "o4-mini")
    raise SystemExit(
        "Configure BROWSER_USE_API_KEY or one supported provider key before running the demo"
    )


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
        llm=build_llm(),
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
