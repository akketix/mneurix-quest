"""
Thumbnail resolution for MNEURIX // QUEST articles.

Policy (config.THUMBNAIL_POLICY): official -> ai -> branded.

  official: Steam capsule image (from appid) or YouTube trailer thumbnail.
            Always accurate, free, zero hallucination.
  ai:       ComfyUI text-to-image with a fact-scoped prompt, gated by a visual
            QA critic. FAIL-CLOSED: if ComfyUI is offline OR the QA critic is
            unavailable OR the image fails QA, we fall through to branded.
  branded:  deterministic 1200x630 cover (radar motif + game title + genre pill)
            rendered via tools/gen-covers.mjs (sharp). Always coherent.

Never returns a random stock photo.
"""

import base64
import json
import logging
import subprocess
import time
from pathlib import Path
from typing import Any

import httpx

from config import (
    BASE_DIR,
    COMFYUI_HOST,
    COVERS_DIR,
    THUMBNAIL_QA_MAX_ATTEMPTS,
    THUMBNAIL_QA_MIN_SCORE,
    THUMBNAIL_POLICY,
)
from ingestion import extract_steam_appid
from verifier import validate_trailer_id

logger = logging.getLogger("thumbnails")

_COVERS_PUBLIC = (
    COVERS_DIR.relative_to(BASE_DIR / "public")
    if (BASE_DIR / "public") in COVERS_DIR.parents
    else None
)
# public/covers -> "/covers"
_PUBLIC_PREFIX = "/" + COVERS_DIR.relative_to(BASE_DIR / "public").as_posix()
_GEN_TOOLS = BASE_DIR / "tools" / "gen-covers.mjs"


def _reachable(url: str, timeout: float = 8.0) -> bool:
    try:
        with httpx.Client(timeout=timeout, follow_redirects=True) as c:
            r = c.head(url, headers={"User-Agent": "MNEURIX-Quest/1.0"})
        return r.status_code < 400 and r.status_code != 405
    except Exception:
        return False


def resolve_steam_screenshot(appid: int, timeout: float = 12.0) -> str | None:
    """Pull a real in-game screenshot (or header) from the Steam appdetails API."""
    try:
        with httpx.Client(
            timeout=timeout, headers={"User-Agent": "MNEURIX-Quest/1.0"}
        ) as c:
            r = c.get(
                f"https://store.steampowered.com/api/appdetails?appids={appid}&l=english"
            )
        data = r.json()
        app = data.get(str(appid), {}).get("data", {}) or {}
        shots = app.get("screenshots") or []
        if shots:
            return shots[0].get("path_full") or shots[0].get("path")
        return app.get("header_image") or app.get("capsule_image")
    except Exception:
        return None


def resolve_wikipedia_image(game_title: str, timeout: float = 12.0) -> str | None:
    """Pull a real showcase image (gameplay screenshot preferred, then cover art)
    for a game from Wikipedia via the images+imageinfo APIs. Free, no API key.
    Skips non-image files and irrelevant assets (flags/logos/cosplay)."""
    if not game_title:
        return None
    ua = "MNEURIX-Quest/1.0 (https://mneurix.quest; hello@mneurix.quest)"
    skip_ext = (".svg", ".webm", ".ogv", ".gif", ".tif", ".tiff", ".ogg", ".pdf")
    skip_words = (
        "flag",
        "logo",
        "map",
        "icon",
        "collage",
        "cosplay",
        "poster",
        "award",
    )

    def score(fname: str) -> int:
        low = fname.lower()
        if any(low.endswith(ext) for ext in skip_ext):
            return -1
        if any(w in low for w in skip_words):
            return -1
        if any(w in low for w in ("gameplay", "screenshot", "screen", "in-game")):
            return 3
        if any(w in low for w in ("cover", "box art", "cover art", "art")):
            return 2
        return 1

    try:
        with httpx.Client(timeout=timeout, headers={"User-Agent": ua}) as c:
            r = c.get(
                "https://en.wikipedia.org/w/api.php",
                params={
                    "action": "query",
                    "format": "json",
                    "titles": game_title,
                    "prop": "images",
                    "imlimit": 20,
                },
            )
            pages = r.json().get("query", {}).get("pages", {})
            files: list[str] = []
            for pg in pages.values():
                for im in pg.get("images") or []:
                    files.append(im.get("title", ""))
            ranked = sorted(
                [(f, score(f)) for f in files], key=lambda x: x[1], reverse=True
            )
            for fname, s in ranked:
                if s < 0:
                    continue
                rr = c.get(
                    "https://en.wikipedia.org/w/api.php",
                    params={
                        "action": "query",
                        "format": "json",
                        "titles": fname,
                        "prop": "imageinfo",
                        "iiprop": "url",
                    },
                )
                for p in rr.json().get("query", {}).get("pages", {}).values():
                    ii = p.get("imageinfo") or []
                    if ii and ii[0].get("url"):
                        return ii[0]["url"]
    except Exception:
        return None
    return None


def resolve_official_thumbnail(facts: dict[str, Any], source_url: str) -> str | None:
    """Return a reachable official image URL, or None."""
    # 1. Steam capsule from the source appid.
    appid = extract_steam_appid(source_url or "")
    if appid:
        capsule = (
            f"https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/header.jpg"
        )
        if _reachable(capsule):
            return capsule
        # Steam appdetails: a real in-game screenshot for this app.
        shot = resolve_steam_screenshot(appid)
        if shot and _reachable(shot):
            return shot
    # 2. YouTube trailer thumbnail from a validated trailer ID.
    tid = (facts.get("trailerId") or "").strip()
    if tid:
        tv = validate_trailer_id(tid, game_title=facts.get("gameTitle"))
        if tv["valid"]:
            for host in ("maxresdefault", "hqdefault"):
                yt = f"https://img.youtube.com/vi/{tid}/{host}.jpg"
                if _reachable(yt):
                    return yt
    # 3. Wikipedia/Wikimedia infobox image for the game (real cover art).
    wiki = resolve_wikipedia_image(facts.get("gameTitle", ""))
    if wiki:
        return wiki
    return None


_IMG_EXT = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}


def _ext_from_url(url: str) -> str:
    path = url.split("?", 1)[0].split("#", 1)[0]
    seg = path.rsplit("/", 1)[-1]
    if "." in seg:
        ext = seg.rsplit(".", 1)[-1].lower()
        if ext.isalpha() and len(ext) <= 5:
            return "." + ext
    return ""


def localize_image(url: str, slug: str, timeout: float = 30.0) -> str | None:
    """Download a remote image into public/covers/<slug><ext>; return the public
    path '/covers/<slug><ext>' or None on failure."""
    if not url or not url.startswith(("http://", "https://")):
        return None
    COVERS_DIR.mkdir(parents=True, exist_ok=True)
    ua = "MNEURIX-Quest/1.0 (https://mneurix.quest; hello@mneurix.quest)"
    try:
        with httpx.Client(
            timeout=timeout, follow_redirects=True, headers={"User-Agent": ua}
        ) as c:
            r = c.get(url)
        if r.status_code >= 400 or not r.content:
            return None
        ext = (
            _ext_from_url(url)
            or _IMG_EXT.get(r.headers.get("content-type", ""), "")
            or ".jpg"
        )
        out = COVERS_DIR / f"{slug}{ext}"
        out.write_bytes(r.content)
        return f"{_PUBLIC_PREFIX}/{slug}{ext}"
    except Exception as e:
        logger.warning(f"localize_image failed for {url}: {e}")
        return None


def _comfyui_reachable() -> bool:
    try:
        with httpx.Client(timeout=5.0) as c:
            r = c.get(f"{COMFYUI_HOST}/system_stats")
        return r.status_code < 400
    except Exception:
        return False


def _ollama_vision_qa(image_path: Path, game_title: str, genre: str) -> bool:
    """Fail-closed visual QA via an Ollama vision model. Returns True only if the
    image is judged a coherent, on-brand cover for the game."""
    try:
        b64 = base64.b64encode(image_path.read_bytes()).decode()
    except Exception as e:
        logger.warning(f"QA: cannot read image {image_path}: {e}")
        return False
    system = "You are a strict visual QA critic for a gaming-news site's article cover images."
    user = (
        f"This is a generated cover image for a {genre} gaming article titled "
        f"'{game_title}'. Rate it 0-100 on: (a) visual coherence (not garbled/blurry/"
        f"nonsensical), (b) relevance to a gaming context. Reply with JSON only: "
        f'{{"score": int, "reason": str}}. Score >= {THUMBNAIL_QA_MIN_SCORE} means acceptable.'
    )
    # Try a vision-capable model; fall through if unavailable.
    for model in ("kimi-k3:cloud", "gemini-3-flash-preview:cloud"):
        try:
            with httpx.Client(timeout=120.0) as c:
                resp = c.post(
                    "http://localhost:11434/api/chat",
                    json={
                        "model": model,
                        "stream": False,
                        "messages": [
                            {"role": "system", "content": system},
                            {"role": "user", "content": user, "images": [b64]},
                        ],
                        "format": "json",
                    },
                )
            if resp.status_code != 200:
                continue
            data = resp.json()
            content = data.get("message", {}).get("content", "")
            parsed = json.loads(content)
            return int(parsed.get("score", 0)) >= THUMBNAIL_QA_MIN_SCORE
        except Exception:
            continue
    return False  # no vision model available -> fail-closed


def generate_ai_thumbnail(
    facts: dict[str, Any], source_text: str, slug: str
) -> str | None:
    """Generate an AI cover via ComfyUI + QA gate. Fail-closed -> None."""
    if not _comfyui_reachable():
        logger.info("AI thumbnail: ComfyUI offline -> falling back.")
        return None
    COVERS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = COVERS_DIR / f"{slug}.png"
    game = facts.get("gameTitle", "the game")
    genre = facts.get("genre", "RTS")
    prompt = (
        f"clean digital key art for a {genre} game '{game}', "
        f"dark cyber aesthetic, teal and slate palette, abstract tactical radar motif, "
        f"no text, no watermark, high detail, cinematic"
    )
    # Minimal ComfyUI txt2img workflow (API format). Generous try/except = fail-closed.
    # Uses SDXL Turbo (sd_xl_turbo_1.0) with Turbo-appropriate sampling: few steps,
    # low CFG, euler. The prior sd_xl_base_1.0 checkpoint is not present in this
    # ComfyUI instance, which caused /prompt 400s and silent branded fallbacks.
    workflow = {
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "seed": abs(hash(prompt)) % (10**9),
                "steps": 8,
                "cfg": 1.5,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": 1.0,
                "model": ["4", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0],
            },
        },
        "4": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": "sd_xl_turbo_1.0.safetensors"},
        },
        "5": {
            "class_type": "EmptyLatentImage",
            "inputs": {"width": 1024, "height": 576, "batch_size": 1},
        },
        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": prompt, "clip": ["4", 1]},
        },
        "7": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": "text, watermark, blurry, deformed, low quality",
                "clip": ["4", 1],
            },
        },
        "8": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["3", 0], "vae": ["4", 2]},
        },
        "9": {
            "class_type": "SaveImage",
            "inputs": {"filename_prefix": slug, "images": ["8", 0]},
        },
    }
    try:
        with httpx.Client(timeout=30.0) as c:
            pr = c.post(f"{COMFYUI_HOST}/prompt", json={"prompt": workflow})
            pr.raise_for_status()
            pid = pr.json()["prompt_id"]
            for _ in range(60):  # poll up to ~5 min
                time.sleep(5)
                h = c.get(f"{COMFYUI_HOST}/history/{pid}").json()
                if pid in h:
                    outputs = h[pid].get("outputs", {})
                    fname = next(
                        iter(next(iter(outputs.values())).get("images", [{}]))
                    )["filename"]
                    sub = next(
                        iter(next(iter(outputs.values())).get("images", [{}]))
                    ).get("subfolder", "")
                    img = c.get(
                        f"{COMFYUI_HOST}/view",
                        params={"filename": fname, "subfolder": sub},
                    )
                    img.raise_for_status()
                    out_path.write_bytes(img.content)
                    break
            else:
                return None
    except Exception as e:
        logger.warning(f"AI thumbnail generation failed: {e}")
        return None
    # QA gate (fail-closed).
    for _ in range(THUMBNAIL_QA_MAX_ATTEMPTS):
        if _ollama_vision_qa(out_path, game, genre):
            return f"{_PUBLIC_PREFIX}/{slug}.png"
        logger.info("AI thumbnail failed QA; would retry.")
        break  # re-generation not wired in this minimal client; fail-closed.
    return None


def branded_thumbnail(slug: str, game_title: str, genre: str) -> str | None:
    """Render a deterministic branded cover PNG via tools/gen-covers.mjs."""
    COVERS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = COVERS_DIR / f"{slug}.png"
    if out_path.exists():
        return f"{_PUBLIC_PREFIX}/{slug}.png"
    try:
        subprocess.run(
            ["node", str(_GEN_TOOLS), "--single", slug, game_title, genre],
            check=True,
            capture_output=True,
            timeout=60,
        )
    except Exception as e:
        logger.error(f"Branded cover generation failed for {slug}: {e}")
        return None
    return f"{_PUBLIC_PREFIX}/{slug}.png" if out_path.exists() else None


def resolve_thumbnail(
    facts: dict[str, Any], source_url: str, slug: str, source_text: str = ""
) -> dict[str, Any]:
    """Resolve the article hero image per policy. Returns {url, source, meta}."""
    result: dict[str, Any] = {"url": "", "source": "none", "meta": {}}
    for tier in THUMBNAIL_POLICY:
        if tier == "official":
            url = resolve_official_thumbnail(facts, source_url)
            if url:
                result.update(url=url, source="official")
                return result
        elif tier == "ai":
            url = generate_ai_thumbnail(facts, source_text, slug)
            if url:
                result.update(url=url, source="ai")
                return result
        elif tier == "branded":
            url = branded_thumbnail(
                slug, facts.get("gameTitle", slug), facts.get("genre", "RPG")
            )
            if url:
                result.update(url=url, source="branded")
                return result
    logger.warning(f"No thumbnail resolved for {slug}.")
    return result
