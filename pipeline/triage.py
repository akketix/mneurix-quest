"""
Triage & Deduplication Layer: Filters out minor hotfixes and duplicate articles.
"""

import hashlib
from typing import List, Dict, Any
from config import MIN_IMPACT_SCORE

_seen_hashes = set()

def compute_hash(title: str) -> str:
    """Computes MD5 hash of normalized title."""
    clean_title = "".join(ch.lower() for ch in title if ch.isalnum())
    return hashlib.md5(clean_title.encode('utf-8')).hexdigest()

def triage_and_filter(raw_articles: List[Dict[str, Any]], mock_scoring: bool = True) -> List[Dict[str, Any]]:
    """
    Deduplicates and evaluates impact score for raw articles.
    """
    triaged_articles = []
    
    for article in raw_articles:
        title_hash = compute_hash(article["title"])
        if title_hash in _seen_hashes:
            continue
        _seen_hashes.add(title_hash)
        
        # Simple heuristic or LLM impact score
        summary_lower = article["summary"].lower()
        title_lower = article["title"].lower()
        
        # Filter low impact updates like minor maintenance or hotfixes
        if any(term in title_lower for term in ["hotfix", "server restart", "maintenance", "small fix", "bugfix"]):
            impact_score = 3
        elif any(term in title_lower or term in summary_lower for term in ["expansion", "reveal", "major update", "beta", "patch", "trailer", "gameplay"]):
            impact_score = 8
        else:
            impact_score = 6

        if impact_score >= MIN_IMPACT_SCORE:
            article["impact_score"] = impact_score
            triaged_articles.append(article)
            
    return triaged_articles
