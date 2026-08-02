"""
CLI Entrypoint for MNEURIX // QUEST Ingestion & Drafting Pipeline.
Usage:
    python run_pipeline.py --dry-run
    python run_pipeline.py --provider ollama
"""

import argparse
import logging
from ingestion import fetch_all_feeds
from triage import triage_and_filter
from agents import extract_facts, generate_editorial_article
from publisher import publish_article

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("main")

def main():
    parser = argparse.ArgumentParser(description="MNEURIX // QUEST Autonomous News Pipeline")
    parser.add_argument("--dry-run", action="store_true", help="Run ingestion & triage without saving or spending tokens")
    parser.add_argument("--provider", type=str, default="mock", choices=["mock", "gemini", "ollama"], help="LLM provider to use")
    parser.add_argument("--limit", type=int, default=3, help="Max articles to process")
    args = parser.parse_args()

    logger.info("Starting MNEURIX // QUEST Agentic News Pipeline...")
    logger.info(f"Target Domain: https://mneurix.quest | Provider: {args.provider}")

    # 1. Ingestion
    raw_articles = fetch_all_feeds()
    if not raw_articles:
        logger.info("No new feeds retrieved. Exiting.")
        return

    # 2. Triage & Deduplication
    triaged = triage_and_filter(raw_articles)
    logger.info(f"Triage complete. {len(triaged)} high-signal articles qualified for drafting.")

    if args.dry-run:
        logger.info("[DRY RUN MODE] Printing qualified articles:")
        for idx, item in enumerate(triaged[:args.limit], 1):
            logger.info(f"  {idx}. [{item['genre']}] (Score: {item['impact_score']}) {item['title']} -> {item['link']}")
        return

    # 3. Fact Extraction & Generation & Publishing
    for article in triaged[:args.limit]:
        logger.info(f"Processing: {article['title']}")
        facts = extract_facts(article, provider=args.provider)
        body = generate_editorial_article(facts, article["summary"], provider=args.provider)
        publish_article(facts, body, article["link"], article["impact_score"])

    logger.info("Pipeline run finished successfully!")

if __name__ == "__main__":
    main()
