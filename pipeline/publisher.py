"""
Publisher Layer: Saves generated articles to site/src/content/news/ with validated YAML frontmatter.
"""

import re
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from config import SITE_NEWS_DIR

logger = logging.getLogger("publisher")

def slugify(text: str) -> str:
    """Generates clean URL slug from title."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s-]+', '-', text).strip('-')
    return text[:60]

def publish_article(facts: Dict[str, Any], body: str, raw_link: str, impact_score: int) -> Path:
    """Writes formatted Markdown file to Astro content collection directory."""
    SITE_NEWS_DIR.mkdir(parents=True, exist_ok=True)
    
    slug = slugify(facts["gameTitle"] + "-" + facts.get("genre", "intel"))
    filename = f"{slug}.md"
    file_path = SITE_NEWS_DIR / filename
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    frontmatter = f"""---
title: "{facts['gameTitle']}: Official Update & Technical Overview"
date: "{date_str}"
gameTitle: "{facts['gameTitle']}"
developer: "{facts['developer']}"
genre: "{facts['genre']}"
platforms: {facts.get('platforms', ['PC'])}
releaseWindow: "{facts.get('releaseWindow', 'TBA')}"
heroImage: "{facts.get('heroImage', '')}"
trailerId: "{facts.get('trailerId', '')}"
impactScore: {impact_score}
sourceUrl: "{raw_link}"
summary: "{facts.get('keyFacts', [''])[0]}"
specs:
  minimum: "{facts.get('minimumSpecs', '')}"
  recommended: "{facts.get('recommendedSpecs', '')}"
---

{body.strip()}
"""

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(frontmatter)
        
    logger.info(f"Published article: {file_path}")
    return file_path
