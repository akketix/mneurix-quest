"""
Ingestion Layer: Fetches RSS feeds for tracked RTS, MMO, and RPG sources.
"""

import logging
from typing import List, Dict, Any
import feedparser

from config import RSS_FEEDS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ingestion")

def fetch_all_feeds() -> List[Dict[str, Any]]:
    """
    Parses all configured RSS feeds and returns normalized raw news items.
    """
    raw_articles = []
    
    for feed_info in RSS_FEEDS:
        url = feed_info["url"]
        genre = feed_info["genre"]
        feed_name = feed_info["name"]
        
        logger.info(f"Fetching feed: {feed_name} ({url})")
        try:
            parsed = feedparser.parse(url)
            for entry in parsed.entries[:5]:  # Fetch 5 latest entries per feed
                raw_articles.append({
                    "source_name": feed_name,
                    "genre": genre,
                    "title": entry.get("title", "").strip(),
                    "link": entry.get("link", "").strip(),
                    "published": entry.get("published", entry.get("updated", "")),
                    "summary": entry.get("summary", entry.get("description", "")).strip()
                })
        except Exception as e:
            logger.error(f"Failed to parse feed {feed_name}: {e}")
            
    logger.info(f"Ingested {len(raw_articles)} raw entries across all feeds.")
    return raw_articles
