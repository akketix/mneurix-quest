"""
CLI entrypoint for the MNEURIX // QUEST ingestion + drafting pipeline, plus an
audit/apply mode for existing articles.

Usage:
  python run_pipeline.py --dry-run
  python run_pipeline.py --provider ollama --limit 3
  python run_pipeline.py --audit                 # report issues in existing articles
  python run_pipeline.py --audit --fix            # apply frontmatter fixes (trailers, images)
  python run_pipeline.py --audit --fix --verify   # also best-effort claim re-verification vs source
"""

import argparse
import json
import logging
import re
from pathlib import Path
from typing import Any

import yaml

from agents import extract_facts, generate_editorial_article
from config import AUDIT_REPORT, SITE_NEWS_DIR
from ingestion import fetch_all_feeds, fetch_source_body
from publisher import publish_article
from thumbnails import resolve_thumbnail
from triage import triage_and_filter
from verifier import (
    audit_claims,
    find_banned_words,
    validate_trailer_id,
)

logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s] %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger("main")

_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)


def _read_article(path: Path) -> tuple[dict[str, Any], str] | None:
    text = path.read_text(encoding="utf-8")
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return None
    try:
        meta = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return None
    return meta, m.group(2)


def audit_existing(fix: bool = False, verify: bool = False) -> None:
    """Scan existing articles; optionally apply frontmatter fixes + best-effort
    claim re-verification. Never rewrites prose structure (only targeted de-slop)."""
    files = sorted(SITE_NEWS_DIR.glob("*.md"))
    logger.info(
        f"Auditing {len(files)} existing articles (fix={fix}, verify={verify})."
    )
    AUDIT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    fh = AUDIT_REPORT.open("w", encoding="utf-8")
    fh.write("# MNEURIX // QUEST — Article Audit Report\n\n")
    fh.write(f"_Scanned {len(files)} articles. fix={fix}, verify={verify}_\n\n")
    fh.flush()
    counts = {
        "articles": 0,
        "stock_images": 0,
        "bad_trailers": 0,
        "banned_hits": 0,
        "covers_rendered": 0,
        "claims_unverifiable": 0,
    }

    for path in files:
        counts["articles"] += 1
        slug = path.stem
        parsed = _read_article(path)
        if not parsed:
            fh.write(f"- ⚠️ {slug}: could not parse frontmatter\n\n")
            fh.flush()
            continue
        meta, body = parsed
        notes: list[str] = []
        changed = False

        # --- trailer validation ---
        tid = str(meta.get("trailerId") or "").strip()
        if tid:
            tv = validate_trailer_id(tid, game_title=str(meta.get("gameTitle", "")))
            if not tv["valid"]:
                counts["bad_trailers"] += 1
                notes.append(f"bad trailerId '{tid}': {tv['reason']}")
                if fix:
                    meta.pop("trailerId", None)
                    changed = True

        # --- hero image: replace stock Unsplash ---
        hero = str(meta.get("heroImage") or "")
        if "images.unsplash.com" in hero:
            counts["stock_images"] += 1
            notes.append("stock Unsplash heroImage")
            if fix:
                thumb = resolve_thumbnail(
                    {
                        "gameTitle": meta.get("gameTitle", slug),
                        "genre": meta.get("genre", "RPG"),
                        "trailerId": meta.get("trailerId", ""),
                    },
                    str(meta.get("sourceUrl", "")),
                    slug,
                )
                if thumb.get("url"):
                    meta["heroImage"] = thumb["url"]
                    if thumb["source"] == "branded":
                        counts["covers_rendered"] += 1
                    notes.append(
                        f"  -> replaced with {thumb['source']}: {thumb['url']}"
                    )
                    changed = True

        # --- banned words (report only; targeted de-slop is a manual review call) ---
        hits = find_banned_words(body)
        if hits:
            counts["banned_hits"] += len(hits)
            notes.append(
                f"banned words: {[h['word'] for h in hits]} (lines {[h['first_line'] for h in hits]}); manual review recommended"
            )

        # --- best-effort claim re-verification vs source ---
        if verify:
            src_url = str(meta.get("sourceUrl") or "")
            src = fetch_source_body(src_url)
            if not src["ok"] or not src["text"].strip():
                counts["claims_unverifiable"] += 1
                notes.append(
                    f"source unreachable/unparseable: {src_url} (claims not verified)"
                )
            else:
                audit = audit_claims(body, src["text"])
                cnt = audit["counts"]
                notes.append(f"claim audit vs source: {cnt}")
                if cnt["unsupported"] or cnt["contradicted"]:
                    counts["claims_unverifiable"] += (
                        cnt["unsupported"] + cnt["contradicted"]
                    )
                    bad = [
                        c
                        for c in audit["claims"]
                        if c.get("verdict") in ("unsupported", "contradicted")
                    ]
                    for c in bad[:5]:
                        notes.append(
                            f"  - [{c.get('verdict')}] {str(c.get('claim', ''))[:80]}"
                        )

        if changed:
            _write_article(path, meta, body)
        flag = "🔧 fixed" if changed else ("⚠️ issues" if notes else "✓ clean")
        fh.write(f"### {slug}\n- status: {flag}\n")
        for n in notes:
            fh.write(f"- {n}\n")
        fh.write("\n")
        fh.flush()

    fh.write("\n## Summary\n")
    for k, v in counts.items():
        fh.write(f"- {k}: {v}\n")
    fh.close()
    logger.info(f"Audit report written to {AUDIT_REPORT}")
    print(f"Audit complete: {counts}")


def _write_article(path: Path, meta: dict[str, Any], body: str) -> None:
    """Rewrite an article preserving body, with updated frontmatter."""
    # Keep field order stable and only include known keys.
    ordered = {}
    for key in [
        "title",
        "date",
        "gameTitle",
        "developer",
        "genre",
        "platforms",
        "releaseWindow",
        "heroImage",
        "trailerId",
        "impactScore",
        "sourceUrl",
        "summary",
    ]:
        if key in meta and meta[key] not in (None, ""):
            ordered[key] = meta[key]
    if "specs" in meta and meta["specs"]:
        ordered["specs"] = meta["specs"]
    fm = yaml.safe_dump(
        ordered, allow_unicode=True, sort_keys=False, default_flow_style=False
    ).strip()
    path.write_text(f"---\n{fm}\n---\n\n{body}", encoding="utf-8")


def run_pipeline(provider: str, limit: int, dry_run: bool) -> None:
    logger.info("Starting MNEURIX // QUEST Agentic News Pipeline...")
    logger.info(f"Target Domain: https://mneurix.quest | Provider: {provider}")

    raw_articles = fetch_all_feeds()
    if not raw_articles:
        logger.info("No new feeds retrieved. Exiting.")
        return

    triaged = triage_and_filter(raw_articles)
    logger.info(
        f"Triage complete. {len(triaged)} high-signal articles qualified for drafting."
    )

    if dry_run:
        logger.info("[DRY RUN MODE] Printing qualified articles:")
        for idx, item in enumerate(triaged[:limit], 1):
            logger.info(
                f"  {idx}. [{item['genre']}] (Score: {item['impact_score']}) {item['title']} -> {item['link']}"
            )
        return

    for article in triaged[:limit]:
        logger.info(f"Processing: {article['title']}")
        source = fetch_source_body(article["link"])
        source_text = source["text"] if source["ok"] else article["summary"]
        if not source["ok"]:
            logger.warning("Source body unavailable; grounding from RSS summary only.")
        facts = extract_facts(article, provider=provider, source_text=source_text)
        body = generate_editorial_article(
            facts, article["summary"], provider=provider, source_text=source_text
        )
        publish_article(
            facts,
            body,
            article["link"],
            article["impact_score"],
            source_text=source_text,
            title=article["title"],
        )

    logger.info("Pipeline run finished successfully!")


def run_seeds(seeds_path: str, provider: str, limit: int) -> None:
    """Generate articles from an explicit JSON seed list [{title, link, genre}].

    Bypasses RSS/triage; fetches each source (Playwright-first) and runs the full
    grounded extraction -> editorial -> verify -> publish chain. Useful when the
    configured RSS feeds are stale or for one-off press-release articles.
    """
    seeds = json.loads(Path(seeds_path).read_text(encoding="utf-8"))
    logger.info(f"Seed mode: {len(seeds)} seeds, provider={provider}.")
    for seed in seeds[:limit]:
        title = str(seed.get("title", "")).strip()
        link = str(seed.get("link", "")).strip()
        genre = str(seed.get("genre", "RPG")).upper()
        logger.info(f"Processing seed: {title} -> {link}")
        source = fetch_source_body(link)
        if not source["ok"] or not source["text"].strip():
            logger.warning(f"Source unavailable for seed; skipping: {link}")
            continue
        source_text = source["text"]
        raw = {"title": title, "summary": "", "source_name": "seed", "genre": genre}
        facts = extract_facts(raw, provider=provider, source_text=source_text)
        facts["gameTitle"] = facts.get("gameTitle") or title
        facts["genre"] = facts.get("genre") or genre
        body = generate_editorial_article(
            facts, raw["summary"], provider=provider, source_text=source_text
        )
        publish_article(
            facts, body, link, 8, source_text=source_text, title=title
        )
    logger.info("Seed run finished.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="MNEURIX // QUEST Autonomous News Pipeline"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ingest & triage without saving or spending tokens",
    )
    parser.add_argument(
        "--provider",
        type=str,
        default="mock",
        choices=["mock", "ollama"],
        help="LLM provider",
    )
    parser.add_argument("--limit", type=int, default=3, help="Max articles to process")
    parser.add_argument(
        "--audit", action="store_true", help="Audit existing src/content/news articles"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="With --audit: apply frontmatter fixes (trailers/images)",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="With --audit: best-effort claim re-verification vs sourceUrl",
    )
    parser.add_argument(
        "--seeds",
        type=str,
        default="",
        help="JSON file of seeds [{title, link, genre}] to generate from (bypasses RSS)",
    )
    args = parser.parse_args()

    if args.seeds:
        run_seeds(args.seeds, provider=args.provider, limit=args.limit)
        return
    if args.audit:
        audit_existing(fix=args.fix, verify=args.verify)
        return
    run_pipeline(provider=args.provider, limit=args.limit, dry_run=args.dry_run)


if __name__ == "__main__":
    main()

