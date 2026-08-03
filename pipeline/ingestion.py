"""
Ingestion Layer: Fetches RSS feeds for tracked RTS, MMO, RPG, and Hardware sources,
and retrieves the full source body for grounding (anti-hallucination).
"""

import logging
import re
from typing import Any, Optional

from bs4 import BeautifulSoup
import feedparser
import httpx

from config import RSS_FEEDS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ingestion")


def _first(value: Any) -> str:
    """Coerce a feedparser field (str | list | None) into a clean string."""
    if value is None:
        return ""
    if isinstance(value, list):
        value = value[0] if value else ""
    return str(value).strip()

# Headers mimic a browser so press/Steam pages serve real content.
_FETCH_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

# Tags that are boilerplate, not article content.
_BOILERPLATE_TAGS = ("script", "style", "noscript", "nav", "footer", "header", "aside", "form")


def fetch_all_feeds() -> list[dict[str, Any]]:
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
                    "title": _first(entry.get("title")),
                    "link": _first(entry.get("link")),
                    "published": _first(entry.get("published") or entry.get("updated")),
                    "summary": _first(entry.get("summary") or entry.get("description")),
                })
        except Exception as e:
            logger.error(f"Failed to parse feed {feed_name}: {e}")

    logger.info(f"Ingested {len(raw_articles)} raw entries across all feeds.")
    return raw_articles


def _extract_text(html: str) -> str:
    """Turn raw HTML into clean, readable plain text for LLM grounding."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(_BOILERPLATE_TAGS):
        tag.decompose()
    text = soup.get_text(separator="\n", strip=True)
    # Collapse excessive blank lines.
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    return "\n".join(lines)


def fetch_source_body(url: str, timeout: float = 15.0) -> dict[str, Any]:
    """
    Fetch the full source page and return readable text for grounding.

    Returns:
        {url, ok, text, final_url} — text is empty/ok=False on failure so
        downstream agents degrade gracefully instead of hallucinating.
    """
    if not url or not url.startswith(("http://", "https://")):
        return {"url": url, "ok": False, "text": "", "final_url": url}
    try:
        with httpx.Client(headers=_FETCH_HEADERS, follow_redirects=True, timeout=timeout) as client:
            resp = client.get(url)
            if resp.status_code >= 400:
                logger.warning(f"Source fetch {url} returned HTTP {resp.status_code}")
                return {"url": url, "ok": False, "text": "", "final_url": str(resp.url)}
            text = _extract_text(resp.text)
            logger.info(f"Fetched source body: {url} -> {len(text)} chars")
            return {"url": url, "ok": bool(text), "text": text, "final_url": str(resp.url)}
    except Exception as e:
        logger.warning(f"Source fetch failed for {url}: {e}")
        return {"url": url, "ok": False, "text": "", "final_url": url}


def extract_steam_appid(url: str) -> Optional[int]:
    """Return the Steam appid from a store/news URL, or None."""
    if not url:
        return None
    m = re.search(r"steam(?:powered|community)\.com/[^/]*app/(\d+)", url)
    if m:
        return int(m.group(1))
    m = re.search(r"/news/app/(\d+)", url)
    if m:
        return int(m.group(1))
    return None