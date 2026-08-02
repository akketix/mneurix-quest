"""
Agentic Layer: Fact Extraction Agent and Journalistic Editorial Agent.
Compatible with Gemini API, OpenAI API format, or local Ollama instances.
"""

import json
import logging
from typing import Dict, Any, Optional
from config import BANNED_WORDS

logger = logging.getLogger("agents")

SYSTEM_FACT_EXTRACTOR = """
You are a precise Gaming Fact Extraction Agent.
Extract game intelligence from press releases into strict JSON.
JSON output fields required:
- gameTitle: string
- developer: string
- genre: "RTS" | "MMO" | "RPG"
- platforms: array of strings (e.g. ["PC", "PS5"])
- releaseWindow: string (e.g. "Q4 2026", "Available Now")
- heroImage: string URL
- trailerId: string YouTube ID (optional)
- minimumSpecs: string (optional)
- recommendedSpecs: string (optional)
- keyFacts: array of 3 bullet point strings
"""

SYSTEM_EDITORIAL_WRITER = f"""
You are an expert Gaming Journalist writing for MNEURIX // QUEST (mneurix.quest).
Your goal is to turn verified game facts into a concise, high-signal article in Markdown.

STRICT JOURNALISTIC GUIDELINES:
1. NEVER use banned AI cliché words: {', '.join(BANNED_WORDS)}.
2. Write with direct, objective, technical prose. Avoid fluff or sensationalized praise.
3. Structure with H2 headings (e.g., "## Core Mechanical Updates", "## Infrastructure & Balance").
4. Keep the article between 250 to 450 words.
"""

def extract_facts(raw_article: Dict[str, Any], provider: str = "mock") -> Dict[str, Any]:
    """Extracts structured facts from raw press text."""
    if provider == "mock":
        return {
            "gameTitle": raw_article.get("title", "Upcoming Title").split(":")[0].strip(),
            "developer": raw_article.get("source_name", "Game Developer"),
            "genre": raw_article.get("genre", "RPG"),
            "platforms": ["PC"],
            "releaseWindow": "2026 Target",
            "heroImage": "https://images.unsplash.com/photo-1542751371-adc38448a05e?q=80&w=1200&auto=format&fit=crop",
            "trailerId": "dQw4w9WgXcQ",
            "minimumSpecs": "Intel i5-8400 / GTX 1060",
            "recommendedSpecs": "Intel i7-12700K / RTX 3070",
            "keyFacts": [
                "Key gameplay balance and system changes detailed in latest press release.",
                "Engine optimization targeting stable tick rates and high player count scenarios.",
                "Public beta testing scheduled for upcoming quarter across major platforms."
            ]
        }
    return {}

def generate_editorial_article(facts: Dict[str, Any], raw_summary: str, provider: str = "mock") -> str:
    """Generates MNEURIX-styled Markdown prose from extracted facts."""
    if provider == "mock":
        bullet_points = "\n".join([f"- **Update Focus**: {fact}" for fact in facts.get("keyFacts", [])])
        return f"""
{facts.get('developer', 'The developer')} has officially published new technical and operational details regarding *{facts.get('gameTitle', 'the project')}*. The update outlines core mechanical balancing, netcode optimization, and release roadmaps.

## Key Mechanical Takeaways

{bullet_points}

## Technical & Engine Scope

The development team confirmed that upcoming performance patches focus on frame pacing, shader pre-compilation, and memory management during high-density combat encounters. 

Additional details regarding future playtest windows and community feedback channels will be published via official developer hubs.
"""
    return ""
