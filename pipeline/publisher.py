"""
Publisher Layer: validates facts, runs the anti-hallucination gate, resolves the
thumbnail, and writes the Astro Markdown article to src/content/news/.

Publication is BLOCKED when:
  - required facts are missing (gameTitle/genre)
  - a direct quote fails grounding (hard gate, per config)
The trailerId is stripped when it fails YouTube oEmbed validation, and specs are
omitted entirely when ungrounded (empty).
"""

import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from config import SITE_NEWS_DIR, VALID_GENRES
from thumbnails import resolve_thumbnail
from verifier import (
    extract_quotes,
    find_banned_words,
    replace_banned_words,
    validate_trailer_id,
    verify_quotes,
)

logger = logging.getLogger("publisher")


def slugify(text: str) -> str:
    """Generate a clean URL slug from text."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s-]+", "-", text).strip("-")
    return text[:60]


def _yaml_list(items: list[str]) -> str:
    return "[" + ", ".join(f'"{i}"' for i in items) + "]"


def publish_article(
    facts: dict[str, Any],
    body: str,
    raw_link: str,
    impact_score: int,
    source_text: str = "",
    slug_override: str | None = None,
    write: bool = True,
) -> Path | None:
    """Validate, gate, resolve thumbnail, and write the article. Returns path or None."""
    # 1. Required-field validation.
    game_title = str(facts.get("gameTitle", "")).strip()
    genre = str(facts.get("genre", "")).upper()
    if not game_title:
        logger.error("Publish blocked: missing gameTitle.")
        return None
    if genre not in VALID_GENRES:
        logger.warning(f"Publish blocked: invalid genre '{genre}'.")
        return None

    slug = slug_override or slugify(f"{game_title}-{genre}")
    if not slug:
        slug = slugify(game_title) or "intel"

    # 2. Trailer validation — strip fake/unresolvable IDs.
    trailer_id = str(facts.get("trailerId", "")).strip()
    if trailer_id:
        tv = validate_trailer_id(trailer_id, game_title=game_title)
        if not tv["valid"]:
            logger.info(f"Stripping invalid trailerId '{trailer_id}': {tv['reason']}")
            trailer_id = ""

    # 3. Thumbnail resolution (official -> ai -> branded).
    thumb = resolve_thumbnail(facts, raw_link, slug, source_text)
    hero_image = thumb.get("url") or str(facts.get("heroImage", "")).strip()
    if not hero_image:
        logger.warning(f"No hero image resolved for {slug}; publishing without one.")
    logger.info(f"Thumbnail for {slug}: {thumb.get('source')} -> {hero_image}")

    # 4. Banned-words enforcement (conservative swaps).
    body, swapped = replace_banned_words(body)
    if swapped:
        logger.info(f"Auto-de-slopped banned words: {swapped}")
    leftover = find_banned_words(body)
    if leftover:
        logger.warning(f"Banned words remain (manual review): {[h['word'] for h in leftover]}")

    # 5. Quote grounding — HARD gate.
    quotes = extract_quotes(body)
    if quotes:
        qv = verify_quotes(quotes, source_text)
        if not qv["pass"]:
            logger.error(
                f"Publish BLOCKED: {len(qv['ungrounded'])} ungrounded quote(s): "
                f"{[q['quote'][:60] for q in qv['ungrounded']]}"
            )
            return None

    if not write:
        return None

    # 6. Write frontmatter (omit specs block + trailerId when ungrounded/empty).
    SITE_NEWS_DIR.mkdir(parents=True, exist_ok=True)
    file_path = SITE_NEWS_DIR / f"{slug}.md"
    date_str = datetime.now().strftime("%Y-%m-%d")
    platforms = facts.get("platforms") or ["PC"]
    summary = str(facts.get("keyFacts", [""])[:1][0] if facts.get("keyFacts") else "") or game_title
    min_spec = str(facts.get("minimumSpecs", "")).strip()
    rec_spec = str(facts.get("recommendedSpecs", "")).strip()
    specs_block = ""
    if min_spec or rec_spec:
        specs_block = (
            "\nspecs:\n"
            f'  minimum: "{min_spec}"\n'
            f'  recommended: "{rec_spec}"\n'
        )
    trailer_line = f'trailerId: "{trailer_id}"\n' if trailer_id else ""

    frontmatter = (
        "---\n"
        f'title: "{game_title}: Official Update & Technical Overview"\n'
        f'date: "{date_str}"\n'
        f'gameTitle: "{game_title}"\n'
        f'developer: "{str(facts.get("developer", "")).strip()}"\n'
        f'genre: "{genre}"\n'
        f"platforms: {_yaml_list(platforms)}\n"
        f'releaseWindow: "{str(facts.get("releaseWindow", "TBA")).strip()}"\n'
        f'heroImage: "{hero_image}"\n'
        f"{trailer_line}"
        f"impactScore: {impact_score}\n"
        f'sourceUrl: "{raw_link}"\n'
        f'summary: "{summary}"\n'
        f"{specs_block}"
        "---\n\n"
        f"{body.strip()}\n"
    )

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(frontmatter)

    logger.info(f"Published article: {file_path}")
    return file_path
