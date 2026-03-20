"""Scheduler for AI Ops Platform agents."""

import asyncio
import logging
from datetime import datetime
from typing import Callable, Awaitable

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

from .supabase import SupabaseRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentScheduler:
    """Scheduler for running AI agents on a schedule."""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.repo = SupabaseRepository()
        self._jobs = {}

    def add_agent_job(
        self,
        agent_name: str,
        func: Callable[[], Awaitable[None]],
        cron_expression: str,
        timezone: str = "Europe/Brussels",
    ):
        """Add a scheduled job for an agent."""
        trigger = CronTrigger.from_crontab(cron_expression, timezone=pytz.timezone(timezone))

        job = self.scheduler.add_job(
            func,
            trigger=trigger,
            id=agent_name,
            name=f"{agent_name}_job",
            replace_existing=True,
        )
        self._jobs[agent_name] = job
        logger.info(f"Scheduled {agent_name} with cron: {cron_expression} ({timezone})")

    def remove_agent_job(self, agent_name: str):
        """Remove a scheduled job."""
        if agent_name in self._jobs:
            self.scheduler.remove_job(agent_name)
            del self._jobs[agent_name]
            logger.info(f"Removed job: {agent_name}")

    def start(self):
        """Start the scheduler."""
        self.scheduler.start()
        logger.info("Scheduler started")

    def shutdown(self):
        """Shutdown the scheduler."""
        self.scheduler.shutdown()
        logger.info("Scheduler shutdown")

    def run_job_now(self, agent_name: str):
        """Manually trigger a job to run immediately."""
        if agent_name in self._jobs:
            job = self._jobs[agent_name]
            job.modify(next_run_time=datetime.now(pytz.UTC))
            logger.info(f"Triggered immediate run for: {agent_name}")


def start_scheduler(
    google_ads_func: Callable[[], Awaitable[None]] = None,
    seo_content_func: Callable[[], Awaitable[None]] = None,
) -> AgentScheduler:
    """Initialize and start the scheduler with agent jobs."""
    scheduler = AgentScheduler()

    # Load settings from Supabase
    settings = scheduler.repo.get_all_settings()

    # Google Ads schedule
    google_ads_settings = settings.get("google_ads_schedule", {})
    if google_ads_settings.get("enabled", True) and google_ads_func:
        scheduler.add_agent_job(
            "google_ads",
            google_ads_func,
            google_ads_settings.get("cron", "0 8 * * *"),
            google_ads_settings.get("timezone", "Europe/Brussels"),
        )

    # SEO Content schedule
    seo_settings = settings.get("seo_content_schedule", {})
    if seo_settings.get("enabled", True) and seo_content_func:
        scheduler.add_agent_job(
            "seo_content",
            seo_content_func,
            seo_settings.get("cron", "0 9 * * 1"),
            seo_settings.get("timezone", "Europe/Brussels"),
        )

    scheduler.start()
    return scheduler
