"""
MNEURIX // QUEST - Pipeline Configuration
Domain target: mneurix.quest
"""

import os
from pathlib import Path

# Base Paths
PIPELINE_DIR = Path(__file__).parent.resolve()
BASE_DIR = PIPELINE_DIR.parent
SITE_NEWS_DIR = BASE_DIR / "src" / "content" / "news"
PUBLIC_DIR = BASE_DIR / "public"
COVERS_DIR = PUBLIC_DIR / "covers"

# Runtime state (persisted dedup + audit reports)
RUNTIME_DIR = PIPELINE_DIR / "runtime"
DEDUP_STORE = RUNTIME_DIR / "seen_hashes.json"
AUDIT_REPORT = RUNTIME_DIR / "audit_report.md"

# Target Domain
TARGET_DOMAIN = "https://mneurix.quest"

# Genre Categories (HARDWARE added — the site ships a Hardware sector)
VALID_GENRES = ["RTS", "MMO", "RPG", "HARDWARE"]

# Ingestion Feeds (Targeting RTS, MMO, RPG, Hardware)
RSS_FEEDS = [
    # RTS Sources
    {"name": "Steam News - Stormgate", "url": "https://store.steampowered.com/news/app/2012510/rss", "genre": "RTS"},
    {"name": "Steam News - Tempest Rising", "url": "https://store.steampowered.com/news/app/1486920/rss", "genre": "RTS"},
    # MMO Sources
    {"name": "World of Warcraft News", "url": "https://worldofwarcraft.blizzard.com/en-us/news/rss", "genre": "MMO"},
    {"name": "Steam News - Guild Wars 2", "url": "https://store.steampowered.com/news/app/1284210/rss", "genre": "MMO"},
    # RPG Sources
    {"name": "Steam News - Path of Exile 2", "url": "https://store.steampowered.com/news/app/2694490/rss", "genre": "RPG"},
    {"name": "Steam News - Titan Quest II", "url": "https://store.steampowered.com/news/app/1154030/rss", "genre": "RPG"},
]

# Anti-AI Cliché & Buzzword Banned Words List
BANNED_WORDS = [
    "delve into", "delve", "testament to", "game-changer", "tapestry",
    "poised to", "nestled", "unwavering", "beacon", "masterpiece",
    "groundbreaking", "breathtaking", "revolutionize", "seamlessly",
]

# Minimum Impact Score threshold to generate article (1 to 10 scale)
MIN_IMPACT_SCORE = 6

# Default LLM Provider Settings
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "glm-5.2:cloud")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Hallucination / grounding controls ------------------------------------------------
# Quote grounding: a direct quote is "grounded" if its best fuzzy ratio vs the
# source text is >= this threshold (0..100, difflib ratio scaled to 100).
QUOTE_GROUND_THRESHOLD = 82
# Hard gate: block publication if any direct quote is ungrounded.
GATE_HARD_ON_QUOTES = True
# Soft gate: flag (do not block) unsupported paraphrased claims.
GATE_SOFT_ON_CLAIMS = True

# Trailer (YouTube) validation via oEmbed.
YOUTUBE_OEMBED = "https://www.youtube.com/oembed"

# Thumbnail resolution policy -------------------------------------------------------
# Order of preference: "official" -> "ai" -> "branded". AI requires ComfyUI; if
# unavailable the resolver degrades to "branded" automatically.
THUMBNAIL_POLICY = ["official", "ai", "branded"]
# AI thumbnail QA gate: reject generations scoring below this (0..100) from the
# adversarial visual critic, retry up to QA_MAX_ATTEMPTS times.
THUMBNAIL_QA_MIN_SCORE = 60
THUMBNAIL_QA_MAX_ATTEMPTS = 2
# ComfyUI endpoint (for AI thumbnail generation).
COMFYUI_HOST = os.getenv("COMFYUI_HOST", "http://localhost:8188")
