"""
MNEURIX // QUEST - Pipeline Configuration
Domain target: mneurix.quest
"""

import os
from pathlib import Path

# Base Paths
PIPELINE_DIR = Path(__file__).parent.resolve()
BASE_DIR = PIPELINE_DIR.parent
SITE_NEWS_DIR = BASE_DIR / "site" / "src" / "content" / "news"

# Target Domain
TARGET_DOMAIN = "https://mneurix.quest"

# Genre Categories
VALID_GENRES = ["RTS", "MMO", "RPG"]

# Ingestion Feeds (Targeting RTS, MMO, RPG)
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
    "groundbreaking", "breathtaking", "revolutionize", "seamlessly"
]

# Minimum Impact Score threshold to generate article (1 to 10 scale)
MIN_IMPACT_SCORE = 6

# Default LLM Provider Settings
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3:latest")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
