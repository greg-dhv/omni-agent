"""SEO Content Agent - combines researcher, writer, and executor."""

import logging
from typing import Any

from agents.base import BaseAgent
from core.models import AgentType
from .researcher import SEOKeywordResearcher
from .executor import SEOContentExecutor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SEOContentAgent(BaseAgent):
    """SEO Content optimization agent.

    This agent:
    1. Researches keyword opportunities
    2. Generates recommendations for content creation
    3. On approval, generates multilingual blog articles
    4. On content approval, sends to client via email
    """

    def __init__(self):
        super().__init__(AgentType.SEO_CONTENT)
        self.researcher = SEOKeywordResearcher()
        self.executor = SEOContentExecutor()

    async def analyze(self) -> list[dict]:
        """Run keyword research and generate recommendations.

        Returns:
            List of keyword opportunity recommendations.
        """
        return await self.researcher.run()

    async def execute(self, recommendation: dict) -> dict:
        """Execute an approved recommendation (generate content).

        Args:
            recommendation: The approved recommendation.

        Returns:
            Action dict recording what was done.
        """
        return await self.executor.execute(recommendation)

    async def process_content_approvals(self):
        """Process approved content (send to client).

        This should be called separately from the main execute flow,
        as content approvals happen after content generation.
        """
        return await self.executor.process_approved_content()


# Convenience functions for the scheduler
async def run_seo_research():
    """Run SEO keyword research (called by scheduler)."""
    agent = SEOContentAgent()
    return await agent.run_analysis()


async def run_seo_executor():
    """Execute approved SEO recommendations (generate content)."""
    agent = SEOContentAgent()
    return await agent.run_executor()


async def run_content_delivery():
    """Send approved content to client."""
    agent = SEOContentAgent()
    return await agent.process_content_approvals()
