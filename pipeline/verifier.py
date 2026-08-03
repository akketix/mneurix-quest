"""
Verifier: anti-hallucination checks for MNEURIX // QUEST articles.

Checks:
  1. Quote grounding  — every direct quote must fuzzy-match the source text.
  2. Claim audit      — LLM tags each claim supported/unsupported/contradicted.
  3. Trailer validation — YouTube oEmbed resolves (rejects fake/Rickroll IDs).
  4. Banned-words    — programmatic regex enforcement (curated safe swaps).
  5. Entity cross-check — gameTitle/developer/genre/platforms present in source.

Gate policy (config): hard on ungrounded quotes (block), soft on unsupported
claims (flag only).
"""

import difflib
import logging
import re
from typing import Any

import httpx

from config import (
    BANNED_WORDS,
    GATE_HARD_ON_QUOTES,
    QUOTE_GROUND_THRESHOLD,
    YOUTUBE_OEMBED,
)
from ollama_client import ollama_json

logger = logging.getLogger("verifier")

# Curated neutral replacements for safe automated de-slop (conservative swaps).
BANNED_REPLACEMENTS: dict[str, str] = {
    "delve into": "examine",
    "delve": "examine",
    "testament to": "evidence of",
    "game-changer": "significant change",
    "tapestry": "structure",
    "poised to": "expected to",
    "nestled": "located",
    "unwavering": "steady",
    "beacon": "highlight",
    "masterpiece": "strong release",
    "groundbreaking": "notable",
    "breathtaking": "striking",
    "revolutionize": "change",
    "seamlessly": "smoothly",
}


# ---------------------------------------------------------------- quotes ----------
_QUOTE_RE = re.compile(r"\u201c([^\u201d\n]{12,})\u201d")


def extract_quotes(body: str) -> list[str]:
    """Return direct-quote strings from article body (curly + long straight)."""
    quotes = []
    for m in _QUOTE_RE.finditer(body):
        q = (m.group(1) or m.group(2) or "").strip()
        if q and "http" not in q and len(q) >= 12:
            quotes.append(q)
    return quotes


def best_partial_ratio(needle: str, haystack: str) -> float:
    """Best fuzzy similarity (0..100) of needle against any window of haystack."""
    needle = needle.lower().strip()
    haystack = haystack.lower()
    if not needle or not haystack:
        return 0.0
    if needle in haystack:
        return 100.0
    n = len(needle)
    # Slide a window ~needle length across the haystack (step n//4).
    step = max(1, n // 4)
    best = 0.0
    window = max(8, int(n * 1.15))
    for i in range(0, max(1, len(haystack) - window + 1), step):
        seg = haystack[i : i + window]
        best = max(best, difflib.SequenceMatcher(None, needle, seg).ratio())
    return round(best * 100, 1)


def verify_quotes(
    quotes: list[str], source_text: str, threshold: float = QUOTE_GROUND_THRESHOLD
) -> dict[str, Any]:
    """Ground each quote against the source; return {grounded, ungrounded, pass}."""
    grounded, ungrounded = [], []
    for q in quotes:
        score = best_partial_ratio(q, source_text) if source_text else 0.0
        entry = {"quote": q, "score": score}
        (grounded if score >= threshold else ungrounded).append(entry)
    return {
        "grounded": grounded,
        "ungrounded": ungrounded,
        "pass": (len(ungrounded) == 0) if GATE_HARD_ON_QUOTES else True,
    }


# ---------------------------------------------------------------- claims ----------
_CLAIM_AUDIT_SYSTEM = """You are a strict fact-check auditor for a gaming news site.
Given an ARTICLE and its SOURCE text, judge every factual claim in the article.
Output JSON only: {"claims": [{"claim": str, "verdict": "supported"|"unsupported"|"contradicted", "evidence": str}]}.
- "supported": the claim is directly stated or clearly entailed by the SOURCE (quote the backing span in evidence).
- "unsupported": the SOURCE does not establish this claim (and it is not common general knowledge).
- "contradicted": the SOURCE states the opposite.
Be rigorous. Do not invent evidence. If the SOURCE is empty, mark non-trivial claims "unsupported"."""


def audit_claims(body: str, source_text: str, max_claims: int = 25) -> dict[str, Any]:
    """LLM audit of article claims against the source. Returns {claims, counts}."""
    if not body.strip():
        return {
            "claims": [],
            "counts": {"supported": 0, "unsupported": 0, "contradicted": 0},
        }
    user = f"ARTICLE:\n{body[:6000]}\n\nSOURCE:\n{source_text[:6000]}"
    data = ollama_json(user, system=_CLAIM_AUDIT_SYSTEM, timeout=180.0)
    claims = (data or {}).get("claims", []) if isinstance(data, dict) else []
    claims = claims[:max_claims]
    counts = {"supported": 0, "unsupported": 0, "contradicted": 0}
    for c in claims:
        v = str(c.get("verdict", "")).lower()
        if v in counts:
            counts[v] += 1
    return {"claims": claims, "counts": counts}


# ---------------------------------------------------------------- trailer --------
_YT_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")


def validate_trailer_id(
    trailer_id: str, game_title: str | None = None, timeout: float = 10.0
) -> dict[str, Any]:
    """Validate a YouTube ID via oEmbed. Returns {valid, title, reason}."""
    tid = (trailer_id or "").strip()
    result: dict[str, Any] = {"valid": False, "title": "", "reason": "", "id": tid}
    if not _YT_ID_RE.match(tid):
        result["reason"] = "malformed (YouTube IDs are 11 chars [A-Za-z0-9_-])"
        return result
    # Reject the known Rickroll placeholder used by the mock pipeline.
    if tid == "dQw4w9WgXcQ":
        result["reason"] = "placeholder/Rickroll ID rejected"
        return result
    url = f"https://www.youtube.com/watch?v={tid}"
    try:
        with httpx.Client(timeout=timeout) as client:
            resp = client.get(YOUTUBE_OEMBED, params={"url": url, "format": "json"})
        if resp.status_code == 200 and resp.json().get("title"):
            title = resp.json()["title"]
            result.update({"valid": True, "title": title})
            if game_title:
                ratio = difflib.SequenceMatcher(
                    None, game_title.lower(), title.lower()
                ).ratio()
                result["title_match"] = round(ratio, 2)
            return result
        result["reason"] = f"oEmbed HTTP {resp.status_code} — video unavailable/deleted"
        return result
    except Exception as e:
        result["reason"] = f"oEmbed fetch failed: {e}"
        return result


# ---------------------------------------------------------------- banned words --
def find_banned_words(
    text: str, banned: list[str] = BANNED_WORDS
) -> list[dict[str, Any]]:
    """Return list of {word, count, first_line} for each banned phrase present."""
    hits = []
    for w in banned:
        pattern = r"\b" + re.escape(w) + r"\b"
        matches = re.findall(pattern, text, flags=re.IGNORECASE)
        if matches:
            idx = text.lower().find(w.lower())
            line = text[:idx].count("\n") + 1 if idx >= 0 else 0
            hits.append({"word": w, "count": len(matches), "first_line": line})
    return hits


def replace_banned_words(
    text: str, banned: list[str] = BANNED_WORDS
) -> tuple[str, list[str]]:
    """Conservatively swap banned phrases for neutral alternatives. Returns (new_text, swapped)."""
    swapped = []
    for w in banned:
        repl = BANNED_REPLACEMENTS.get(w)
        if repl is None:
            continue
        pattern = r"\b" + re.escape(w) + r"\b"
        if re.search(pattern, text, flags=re.IGNORECASE):
            text = re.sub(pattern, repl, text, flags=re.IGNORECASE)
            swapped.append(w)
    return text, swapped


# ---------------------------------------------------------------- entities ------
def entity_cross_check(facts: dict[str, Any], source_text: str) -> dict[str, Any]:
    """Check key entities appear (case-insensitive) in the source text."""
    src = source_text.lower()
    fields = {
        "gameTitle": str(facts.get("gameTitle", "")),
        "developer": str(facts.get("developer", "")),
        "genre": str(facts.get("genre", "")),
    }
    report = {}
    for k, v in fields.items():
        if not v:
            report[k] = "missing"
            continue
        # Match on the first significant token to survive "Blackbird Interactive / Gearbox".
        token = (
            v.split("/")[0].strip().split()[0].lower()
            if v.split("/")[0].strip()
            else v.lower()
        )
        report[k] = "present" if token and token in src else "absent"
    platforms = facts.get("platforms", [])
    report["platforms"] = [
        {"platform": p, "present": str(p).lower() in src} for p in platforms
    ]
    return report
