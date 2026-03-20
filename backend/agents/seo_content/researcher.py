"""SEO Keyword Researcher - identifies keyword opportunities."""

import json
import logging
import os
from typing import Any

import anthropic
from dotenv import load_dotenv

from .prompts import (
    KEYWORD_RESEARCH_SYSTEM,
    KEYWORD_RESEARCH_PROMPT,
    format_gsc_data,
    format_competitor_data,
)
from core.models import Recommendation, AgentType, Priority
from core.supabase import SupabaseRepository

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SEOKeywordResearcher:
    """Researches SEO keyword opportunities using Claude."""

    def __init__(self):
        self.claude = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self.repo = SupabaseRepository()

    def get_gsc_data(self) -> list[dict]:
        """Get Google Search Console data.

        In a real implementation, this would connect to GSC API.
        For now, returns placeholder data.
        """
        # TODO: Implement GSC API integration
        # This would typically use google-api-python-client
        logger.info("GSC integration not yet implemented - using placeholder")
        return []

    def get_competitor_data(self) -> list[dict]:
        """Get competitor keyword data.

        In a real implementation, this would use Ahrefs/SEMrush API.
        For now, returns placeholder data.
        """
        # TODO: Implement Ahrefs/SEMrush API integration
        logger.info("Competitor data integration not yet implemented - using placeholder")
        return []

    def get_manual_keywords(self) -> list[str]:
        """Get manually specified seed keywords from settings."""
        settings = self.repo.get_setting("seo_content") or {}
        return settings.get("seed_keywords", [
            "online casino belgium",
            "best casino bonuses",
            "legal gambling belgium",
            "casino games guide",
        ])

    async def research_keywords(self) -> dict[str, Any]:
        """Research keyword opportunities using Claude.

        Returns:
            Parsed JSON with keyword opportunities.
        """
        logger.info("Researching keyword opportunities...")

        # Gather data
        gsc_data = self.get_gsc_data()
        competitor_data = self.get_competitor_data()
        seed_keywords = self.get_manual_keywords()

        # Build prompt
        trends_data = f"Seed keywords to explore: {', '.join(seed_keywords)}"

        prompt = KEYWORD_RESEARCH_PROMPT.format(
            gsc_data=format_gsc_data(gsc_data) if gsc_data else "No GSC data - focus on seed keywords",
            competitor_data=format_competitor_data(competitor_data) if competitor_data else "No competitor data available",
            trends_data=trends_data,
        )

        # Call Claude
        response = self.claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=KEYWORD_RESEARCH_SYSTEM,
            messages=[{"role": "user", "content": prompt}],
        )

        response_text = response.content[0].text

        # Parse JSON
        json_start = response_text.find("{")
        json_end = response_text.rfind("}") + 1

        if json_start == -1:
            logger.error("No JSON found in response")
            return {"summary": response_text, "opportunities": []}

        try:
            result = json.loads(response_text[json_start:json_end])
            logger.info(f"Found {len(result.get('opportunities', []))} keyword opportunities")
            return result
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse response: {e}")
            return {"summary": response_text, "opportunities": []}

    def create_recommendations(self, research_result: dict[str, Any]) -> list[dict]:
        """Convert keyword research to recommendations.

        Args:
            research_result: Parsed JSON from Claude.

        Returns:
            List of recommendation dicts.
        """
        recommendations = []

        priority_map = {
            "high": Priority.HIGH,
            "medium": Priority.MEDIUM,
            "low": Priority.LOW,
        }

        for opp in research_result.get("opportunities", []):
            recommendation = Recommendation(
                agent=AgentType.SEO_CONTENT,
                type="keyword_opportunity",
                priority=priority_map.get(opp.get("priority", "medium"), Priority.MEDIUM),
                title=f"Target keyword: {opp.get('keyword')}",
                summary=opp.get("suggested_topic"),
                details={
                    "keyword": opp.get("keyword"),
                    "search_volume": opp.get("search_volume"),
                    "keyword_difficulty": opp.get("keyword_difficulty"),
                    "intent": opp.get("intent"),
                    "suggested_topic": opp.get("suggested_topic"),
                    "notes": opp.get("notes"),
                },
            )
            recommendations.append(recommendation.to_db_dict())

        return recommendations

    async def run(self) -> list[dict]:
        """Run the full keyword research pipeline.

        Returns:
            List of recommendation dicts.
        """
        research = await self.research_keywords()
        recommendations = self.create_recommendations(research)
        return recommendations
