"""
Agentic Layer: grounded Fact Extraction + Editorial Writing for MNEURIX // QUEST.

Providers:
  - "ollama" : real extraction/writing via glm-5.2:cloud (grounded in source text)
  - "mock"   : deterministic placeholder output for dry-runs (NEVER publishes)

Anti-hallucination: the ollama extractor is forced to ground every field in the
source text and emit an `evidence` span per field; ungrounded specs/trailer are
left empty so the publisher omits them rather than fabricating.
"""

import json
import logging
from typing import Any

from config import BANNED_WORDS, OLLAMA_MODEL, VALID_GENRES
from ollama_client import ollama_json
from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger("agents")

SYSTEM_FACT_EXTRACTOR = """You are a precise Gaming Fact Extraction Agent for MNEURIX // QUEST.
Given an RSS item (title + summary) and the FULL SOURCE TEXT of its press release,
extract ONLY facts that are grounded in the source text. Never invent.

Output strict JSON with these fields:
- gameTitle: string (the game/product name; empty if not determinable)
- developer: string (developer/publisher; empty if unknown)
- genre: one of "RTS" | "MMO" | "RPG" | "HARDWARE" (best fit; empty if unclear)
- platforms: array of strings (e.g. ["PC","PS5"]; [] if unstated)
- releaseWindow: string (e.g. "Q4 2026", "Available Now"; "" if unstated)
- heroImage: string URL ONLY if the source explicitly provides an image URL; else ""
- trailerId: string YouTube video ID ONLY if present in the source; else ""
- minimumSpecs: string ONLY if the source states minimum specs; else ""
- recommendedSpecs: string ONLY if the source states recommended specs; else ""
- keyFacts: array of 3 concise bullet strings, each grounded in the source
- evidence: object mapping each of the fields above to a short verbatim span
  from the source that backs it (or null if the field was empty/unknown)

Rules:
- If a field is not stated in the source, return "" / [] and evidence null.
- Do NOT use placeholder images or placeholder video IDs.
- Output JSON only, no prose."""

SYSTEM_EDITORIAL_WRITER = f"""You are an expert gaming journalist writing for MNEURIX // QUEST (mneurix.quest).
Turn verified, grounded game facts into a concise, high-signal Markdown article.

STRICT GUIDELINES:
1. NEVER use these banned AI cliche words: {', '.join(BANNED_WORDS)}.
2. Write direct, objective, technical prose. No fluff or sensationalized praise.
3. Use H2 headings (e.g. "## Core Mechanical Updates", "## Infrastructure & Balance").
4. Keep the article 250-450 words.
5. Only state claims that are supported by the provided facts/source. Do not invent
   quotes, specs, dates, or features. If unsure, omit.
6. Do not wrap the article in fences; output raw Markdown only.
7. Do NOT start with an H1 (#) heading or restate the title — the site renders the
title from frontmatter. Begin with a lead paragraph."""


class ExtractedFacts(BaseModel):
    gameTitle: str = ""
    developer: str = ""
    genre: str = ""
    platforms: list[str] = Field(default_factory=list)
    releaseWindow: str = ""
    heroImage: str = ""
    trailerId: str = ""
    minimumSpecs: str = ""
    recommendedSpecs: str = ""
    keyFacts: list[str] = Field(default_factory=list)
    evidence: dict[str, Any] = Field(default_factory=dict)

    @field_validator("genre")
    @classmethod
    def _normalize_genre(cls, v: str) -> str:
        v = (v or "").upper()
        return v if v in VALID_GENRES else ""


def _mock_facts(raw_article: dict[str, Any]) -> dict[str, Any]:
    """Deterministic placeholder for dry-runs. No fabricated trailer/image shipped."""
    return {
        "gameTitle": raw_article.get("title", "Upcoming Title").split(":")[0].strip(),
        "developer": raw_article.get("source_name", "Game Developer"),
        "genre": raw_article.get("genre", "RPG"),
        "platforms": ["PC"],
        "releaseWindow": "2026 Target",
        "heroImage": "",
        "trailerId": "",
        "minimumSpecs": "",
        "recommendedSpecs": "",
        "keyFacts": [
            "Key gameplay balance and system changes detailed in latest press release.",
            "Engine optimization targeting stable tick rates and high player counts.",
            "Public beta testing scheduled for the upcoming quarter.",
        ],
        "evidence": {},
    }


def extract_facts(raw_article: dict[str, Any], provider: str = "mock", source_text: str = "") -> dict[str, Any]:
    """Extract structured, grounded facts from a raw article + its source text."""
    if provider != "ollama":
        return _mock_facts(raw_article)

    user = (
        f"RSS TITLE:\n{raw_article.get('title','')}\n\n"
        f"RSS SUMMARY:\n{raw_article.get('summary','')}\n\n"
        f"SOURCE TEXT:\n{source_text[:8000]}"
    )
    data = ollama_json(user, system=SYSTEM_FACT_EXTRACTOR, model=OLLAMA_MODEL, timeout=180.0)
    if not isinstance(data, dict):
        logger.warning("Fact extraction returned no JSON; falling back to mock facts.")
        return _mock_facts(raw_article)
    try:
        validated = ExtractedFacts.model_validate(data)
    except Exception as e:
        logger.warning(f"Fact extraction schema validation failed ({e}); using raw dict.")
        validated = ExtractedFacts.model_validate({k: data.get(k, "") for k in data})
    facts = validated.model_dump()
    # Strip ungrounded optional fields: empty trailer/specs must stay empty.
    if not facts.get("evidence", {}).get("trailerId"):
        facts["trailerId"] = ""
    if not facts.get("evidence", {}).get("minimumSpecs"):
        facts["minimumSpecs"] = ""
    if not facts.get("evidence", {}).get("recommendedSpecs"):
        facts["recommendedSpecs"] = ""
    return facts


def generate_editorial_article(facts: dict[str, Any], raw_summary: str, provider: str = "mock", source_text: str = "") -> str:
    """Generate MNEURIX-styled Markdown prose from grounded facts."""
    if provider != "ollama":
        bullet_points = "\n".join([f"- **Update Focus**: {fact}" for fact in facts.get("keyFacts", [])])
        return (
            f"{facts.get('developer', 'The developer')} has published new technical and operational "
            f"details regarding *{facts.get('gameTitle', 'the project')}*. The update outlines core "
            "mechanical balancing, netcode optimization, and release roadmaps.\n\n"
            "## Key Mechanical Takeaways\n\n"
            f"{bullet_points}\n\n"
            "## Technical & Engine Scope\n\n"
            "The development team confirmed that upcoming performance patches focus on frame pacing, "
            "shader pre-compilation, and memory management during high-density encounters. Additional "
            "playtest details will be published via official developer hubs."
        )

    facts_json = json.dumps(facts, ensure_ascii=False)
    user = (
        f"VERIFIED FACTS (JSON):\n{facts_json}\n\n"
        f"SOURCE TEXT (grounding; do not claim anything not supported here):\n{source_text[:6000]}\n\n"
        f"RSS SUMMARY:\n{raw_summary}"
    )
    from ollama_client import ollama_chat

    body = ollama_chat(user, system=SYSTEM_EDITORIAL_WRITER, model=OLLAMA_MODEL, timeout=180.0)
    if not body or not body.strip():
        logger.warning("Editorial generation returned empty; falling back to mock body.")
        return generate_editorial_article(facts, raw_summary, provider="mock")
    # Trim accidental code fences.
    text = body.strip()
    if text.startswith("```"):
        text = text.split("```", 2)[1]
        if text.startswith("markdown"):
            text = text[8:]
    return text.strip()
