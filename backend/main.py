"""AI Ops Platform - Main Entry Point.

This script runs the agent scheduler and executor polling loop.

Usage:
    python main.py              # Run scheduler + executor loop
    python main.py --analyze    # Run analysis only (no scheduling)
    python main.py --execute    # Run executor only (process approvals)
"""

import asyncio
import argparse
import logging
import signal
import sys
from datetime import datetime

from dotenv import load_dotenv

from core.scheduler import start_scheduler
from core.supabase import SupabaseRepository
from agents.google_ads.agent import run_google_ads_analysis, run_google_ads_executor
from agents.seo_content.agent import run_seo_research, run_seo_executor, run_content_delivery

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Global flag for graceful shutdown
shutdown_flag = False


def signal_handler(signum, frame):
    """Handle shutdown signals."""
    global shutdown_flag
    logger.info("Shutdown signal received...")
    shutdown_flag = True


async def executor_polling_loop(interval: int = 30):
    """Poll for approved recommendations and execute them.

    Args:
        interval: Seconds between polls.
    """
    logger.info(f"Starting executor polling loop (interval: {interval}s)")
    repo = SupabaseRepository()

    while not shutdown_flag:
        try:
            # Check for approved Google Ads recommendations
            google_ads_approved = repo.get_approved_recommendations("google_ads")
            if google_ads_approved:
                logger.info(f"Found {len(google_ads_approved)} approved Google Ads recommendations")
                result = await run_google_ads_executor()
                logger.info(f"Google Ads executor result: {result}")

            # Check for approved SEO recommendations (generate content)
            seo_approved = repo.get_approved_recommendations("seo_content")
            if seo_approved:
                logger.info(f"Found {len(seo_approved)} approved SEO recommendations")
                result = await run_seo_executor()
                logger.info(f"SEO executor result: {result}")

            # Check for approved content (send to client)
            result = await run_content_delivery()
            if result.get("sent", 0) > 0:
                logger.info(f"Content delivery result: {result}")

        except Exception as e:
            logger.error(f"Executor loop error: {e}")

        # Wait for next poll
        await asyncio.sleep(interval)


async def run_analysis_only():
    """Run all agent analyses once."""
    logger.info("Running analysis for all agents...")

    # Google Ads
    try:
        logger.info("Running Google Ads analysis...")
        result = await run_google_ads_analysis()
        logger.info(f"Google Ads analysis complete: {result}")
    except Exception as e:
        logger.error(f"Google Ads analysis failed: {e}")

    # SEO Research
    try:
        logger.info("Running SEO keyword research...")
        result = await run_seo_research()
        logger.info(f"SEO research complete: {result}")
    except Exception as e:
        logger.error(f"SEO research failed: {e}")


async def run_executor_only():
    """Run executors once for all agents."""
    logger.info("Running executors for all agents...")

    # Google Ads
    try:
        result = await run_google_ads_executor()
        logger.info(f"Google Ads executor: {result}")
    except Exception as e:
        logger.error(f"Google Ads executor failed: {e}")

    # SEO Content
    try:
        result = await run_seo_executor()
        logger.info(f"SEO executor: {result}")
    except Exception as e:
        logger.error(f"SEO executor failed: {e}")

    # Content Delivery
    try:
        result = await run_content_delivery()
        logger.info(f"Content delivery: {result}")
    except Exception as e:
        logger.error(f"Content delivery failed: {e}")


async def main(args):
    """Main entry point."""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    if args.analyze:
        # Run analysis only
        await run_analysis_only()
        return

    if args.execute:
        # Run executor only
        await run_executor_only()
        return

    # Default: Run scheduler + executor loop
    logger.info("Starting AI Ops Platform...")
    logger.info(f"Time: {datetime.now().isoformat()}")

    # Start the scheduler with agent functions
    scheduler = start_scheduler(
        google_ads_func=run_google_ads_analysis,
        seo_content_func=run_seo_research,
    )

    try:
        # Run executor polling loop
        await executor_polling_loop(interval=30)
    finally:
        logger.info("Shutting down scheduler...")
        scheduler.shutdown()
        logger.info("AI Ops Platform stopped.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Ops Platform")
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Run analysis for all agents once and exit",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Run executors for approved recommendations once and exit",
    )
    args = parser.parse_args()

    asyncio.run(main(args))
