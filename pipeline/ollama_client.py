"""
Shared Ollama chat helper used by the extraction + verification agents.
Targets the local Ollama gateway (cloud models such as glm-5.2:cloud) — no API key.
"""

import json
import logging
from typing import Any

import httpx

from config import OLLAMA_HOST, OLLAMA_MODEL

logger = logging.getLogger("llm")


def ollama_chat(
    user: str,
    system: str = "",
    model: str = OLLAMA_MODEL,
    json_mode: bool = False,
    timeout: float = 180.0,
) -> str | None:
    """Send a chat completion to Ollama and return the assistant text (or None)."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": user})
    payload: dict[str, Any] = {"model": model, "messages": messages, "stream": False}
    if json_mode:
        payload["format"] = "json"
    try:
        with httpx.Client(timeout=timeout) as client:
            resp = client.post(f"{OLLAMA_HOST}/api/chat", json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["message"]["content"]
    except Exception as e:
        logger.error(f"ollama_chat failed ({model}): {e}")
        return None


def ollama_json(
    user: str,
    system: str = "",
    model: str = OLLAMA_MODEL,
    timeout: float = 180.0,
) -> Any | None:
    """Chat expecting JSON output; returns the parsed object or None."""
    raw = ollama_chat(user, system=system, model=model, json_mode=True, timeout=timeout)
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Some models wrap JSON in prose / fences — try to salvage.
        text = raw.strip()
        if text.startswith("```"):
            text = text.split("```", 2)[1]
            if text.startswith("json"):
                text = text[4:]
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            logger.warning(f"ollama_json: could not parse response: {raw[:200]}")
            return None
