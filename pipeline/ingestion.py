"""
Ingestion Layer: fetches RSS feeds and retrieves full, JS-rendered source bodies
for grounding (anti-hallucination).

Source fetch strategy (per URL):
  1. Playwright headless render -> enhanced text extraction from the live DOM.
     (Activates only if the optional `playwright` package + a browser are
     available; not required for the pipeline to run.)
  2. Fallback: httpx GET -> enhanced static extraction that salvages content from
     JSON-LD blocks, __NEXT_DATA__/__NUXT__ hydration JSON, and OpenGraph meta
     before falling back to visible text — so JS-heavy sites still yield usable
     grounding text without a browser.
"""

import contextlib
import json
import logging
import re
from typing import Any

from bs4 import BeautifulSoup
import feedparser
import httpx

from config import RSS_FEEDS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ingestion")

_FETCH_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

_BOILERPLATE_TAGS = ("script", "style", "noscript", "nav", "footer", "header", "aside", "form")

# Playwright is an OPTIONAL enhancement; import lazily and tolerate absence.
_PW = None
try:  # pragma: no cover
    from playwright.sync_api import sync_playwright as _pw  # type: ignore

    _PW = _pw
except Exception:  # pragma: no cover
    _pw = None


def fetch_all_feeds() -> list[dict[str, Any]]:
    """Parse all configured RSS feeds and return normalized raw news items."""
    raw_articles = []
    for feed_info in RSS_FEEDS:
        url = feed_info["url"]
        genre = feed_info["genre"]
        feed_name = feed_info["name"]
        logger.info(f"Fetching feed: {feed_name} ({url})")
        try:
            parsed = feedparser.parse(url)  # type: ignore[name-defined]
            for entry in parsed.entries[:5]:
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


def _first(value: Any) -> str:
    """Coerce a feedparser field (str | list | None) into a clean string."""
    if value is None:
        return ""
    if isinstance(value, list):
        value = value[0] if value else ""
    return str(value).strip()


def _walk_jsonld(node: Any):
    """Yield every dict inside a JSON-LD structure."""
    if isinstance(node, dict):
        yield node
        for v in node.values():
            yield from _walk_jsonld(v)
    elif isinstance(node, list):
        for item in node:
            yield from _walk_jsonld(item)


def _collect_long_strings(node: Any, min_len: int = 60) -> list[str]:
    """Recurse a JSON tree and collect long text-like strings (hydration content)."""
    out: list[str] = []
    if isinstance(node, str):
        if len(node) >= min_len and not node.startswith("{"):
            out.append(node)
    elif isinstance(node, dict):
        for v in node.values():
            out.extend(_collect_long_strings(v, min_len))
    elif isinstance(node, list):
        for item in node:
            out.extend(_collect_long_strings(item, min_len))
    return out


def _extract_text(html: str) -> str:
    """Enhanced readable-text extraction (works on rendered OR raw HTML)."""
    soup = BeautifulSoup(html, "html.parser")
    chunks: list[str] = []

    # 1. JSON-LD articleBody / description / text.
    for s in soup.find_all("script", attrs={"type": "application/ld+json"}):
        raw = s.string or s.get_text() or ""
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        for obj in _walk_jsonld(data):
            for key in ("articleBody", "text", "description", "body"):
                v = obj.get(key)
                if isinstance(v, str) and len(v) > 40:
                    chunks.append(v)

    # 2. Next.js / Nuxt hydration payloads.
    for sid in ("__NEXT_DATA__", "__NUXT__", "__NUXT_DATA__"):
        s = soup.find("script", attrs={"id": sid})
        if s:
            try:
                data = json.loads(s.string or "{}")
            except json.JSONDecodeError:
                continue
            chunks.extend(_collect_long_strings(data, min_len=60))

    # 3. OpenGraph / description meta.
    for prop in ("og:description", "description"):
        m = soup.find("meta", attrs={"property": prop}) or soup.find("meta", attrs={"name": prop})
        content = str(m.get("content") or "") if m else ""
        if len(content) > 40:
            chunks.append(content)

    # 4. Main content region, else whole doc (boilerplate stripped).
    for tag in soup(_BOILERPLATE_TAGS):
        tag.decompose()
    main = soup.find("article") or soup.find("main") or soup.find(attrs={"role": "main"})
    chunks.append((main or soup).get_text(separator="\n", strip=True))

    # Dedupe by leading window, preserve order.
    seen: set[str] = set()
    out: list[str] = []
    for c in chunks:
        c = c.strip()
        if len(c) < 20:
            continue
        key = c[:80]
        if key in seen:
            continue
        seen.add(key)
        out.append(c)
    return "\n".join(out)


def _render_with_playwright(url: str, timeout: float = 25.0) -> str | None:
    """Render a URL with headless Chromium and return the live DOM HTML, or None."""
    if _PW is None:
        return None
    try:
        with _PW() as p:  # type: ignore[misc]
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(user_agent=_FETCH_HEADERS["User-Agent"])
            page.goto(url, timeout=int(timeout * 1000), wait_until="domcontentloaded")
            with contextlib.suppress(Exception):
                page.wait_for_load_state("networkidle", timeout=8000)
            html = page.content()
            browser.close()
            return html
    except Exception as e:
        logger.warning(f"Playwright render failed for {url}: {e}")
        return None


def fetch_source_body(url: str, timeout: float = 20.0) -> dict[str, Any]:
    """Fetch a source page (Playwright first, httpx fallback) and return readable text."""
    if not url or not url.startswith(("http://", "https://")):
        return {"url": url, "ok": False, "text": "", "final_url": url}

    # 1. Try a JS-rendered fetch.
    rendered = _render_with_playwright(url, timeout=timeout)
    if rendered:
        text = _extract_text(rendered)
        if len(text) >= 120:
            logger.info(f"Fetched (playwright): {url} -> {len(text)} chars")
            return {"url": url, "ok": True, "text": text, "final_url": url, "method": "playwright"}

    # 2. Fallback to a plain HTTP GET + enhanced static extraction.
    try:
        with httpx.Client(headers=_FETCH_HEADERS, follow_redirects=True, timeout=timeout) as client:
            resp = client.get(url)
            if resp.status_code >= 400:
                logger.warning(f"Source fetch {url} returned HTTP {resp.status_code}")
            else:
                text = _extract_text(resp.text)
                if text:
                    logger.info(f"Fetched (httpx): {url} -> {len(text)} chars")
                    return {"url": url, "ok": True, "text": text, "final_url": str(resp.url), "method": "httpx"}
    except Exception as e:
        logger.warning(f"Source fetch failed for {url}: {e}")

    return {"url": url, "ok": False, "text": "", "final_url": url, "method": "none"}


def extract_steam_appid(url: str) -> int | None:
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

