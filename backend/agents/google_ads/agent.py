"""Google Ads Agent - combines analyst and executor."""

import logging
from typing import Any

from agents.base import BaseAgent
from core.models import AgentType
from .analyst import GoogleAdsAnalyst
from .executor import GoogleAdsExecutor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GoogleAdsAgent(BaseAgent):
    """Google Ads optimization agent.

    This agent:
    1. Pulls performance data from Google Ads API
    2. Analyzes data with Claude to find optimization opportunities
    3. Generates recommendations for human approval
    4. Executes approved recommendations via Google Ads API
    """

    def __init__(self, config_path: str = "config/google-ads.yaml"):
        super().__init__(AgentType.GOOGLE_ADS)
        self.analyst = GoogleAdsAnalyst(config_path)
        self.executor = GoogleAdsExecutor(config_path)
        self.config_path = config_path

    async def analyze(self) -> list[dict]:
        """Run analysis and generate recommendations.

        Returns:
            List of recommendation dicts ready for database insertion.
        """
        # Get settings from database
        settings = self.repo.get_setting("google_ads") or {}
        days = settings.get("lookback_days", 7)
        high_cost_threshold = settings.get("high_cost_no_conversion_threshold", 50)
        low_ctr_threshold = settings.get("low_ctr_threshold", 1.0)

        # Run analysis
        recommendations = await self.analyst.run(
            days=days,
            high_cost_threshold=high_cost_threshold,
            low_ctr_threshold=low_ctr_threshold,
        )

        return recommendations

    async def execute(self, recommendation: dict) -> dict:
        """Execute an approved recommendation.

        Args:
            recommendation: The approved recommendation to execute.

        Returns:
            Action dict recording what was done.
        """
        return self.executor.execute(recommendation)


# Convenience functions for the scheduler
async def run_google_ads_analysis():
    """Run Google Ads analysis (called by scheduler)."""
    agent = GoogleAdsAgent()
    return await agent.run_analysis()


async def run_google_ads_executor():
    """Execute approved Google Ads recommendations (called by scheduler/polling)."""
    agent = GoogleAdsAgent()
    return await agent.run_executor()
