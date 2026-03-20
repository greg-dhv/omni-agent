"""Google Ads Analyst - analyzes performance and generates recommendations."""

import json
import logging
import os
from datetime import datetime
from typing import Any

import anthropic
from dotenv import load_dotenv

from .client import GoogleAdsAPIClient
from .prompts import (
    get_system_prompt,
    ANALYSIS_PROMPT,
    format_campaign_data,
    format_keyword_data,
    format_search_term_data,
    format_ad_data,
    format_converting_search_terms,
)
from core.models import Recommendation, AgentType, Priority, PerformanceSnapshot
from core.supabase import SupabaseRepository

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GoogleAdsAnalyst:
    """Analyzes Google Ads performance data using Claude."""

    def __init__(self, config_path: str = "config/google-ads.yaml"):
        self.ads_client = GoogleAdsAPIClient(config_path)
        self.claude = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self.repo = SupabaseRepository()

    def pull_data(self, days: int = 7) -> dict[str, list[dict]]:
        """Pull all performance data from Google Ads API.

        Args:
            days: Number of days to look back.

        Returns:
            Dict with campaign, keyword, search_term, ad, and converting_search_terms data.
        """
        logger.info(f"Pulling Google Ads data for last {days} days...")

        data = {
            "campaigns": self.ads_client.get_campaign_performance(days),
            "keywords": self.ads_client.get_keyword_performance(days),
            "search_terms": self.ads_client.get_search_terms(days),
            "ads": self.ads_client.get_ad_performance(days),
            "converting_search_terms": self.ads_client.get_converting_search_terms(days, min_conversions=1),
        }

        logger.info(
            f"Pulled: {len(data['campaigns'])} campaigns, "
            f"{len(data['keywords'])} keywords, "
            f"{len(data['search_terms'])} search terms, "
            f"{len(data['ads'])} ads, "
            f"{len(data['converting_search_terms'])} converting search terms"
        )

        return data

    def save_performance_snapshot(self, data: dict[str, list[dict]], days: int = 30) -> None:
        """Save daily performance snapshots to database.

        Pulls daily metrics from Google Ads API and saves each day as a separate snapshot.
        This enables accurate time-range filtering in the frontend.
        """
        logger.info(f"Pulling daily metrics for last {days} days...")
        daily_metrics = self.ads_client.get_daily_metrics(days)

        logger.info(f"Saving {len(daily_metrics)} daily snapshots...")
        for day_data in daily_metrics:
            snapshot = PerformanceSnapshot(
                date=day_data["date"],
                source="google_ads",
                metrics={
                    "cost": day_data["cost"],
                    "clicks": day_data["clicks"],
                    "conversions": day_data["conversions"],
                    "impressions": day_data["impressions"],
                    "ctr": day_data["ctr"],
                    "cpc": day_data["cpc"],
                },
            )
            self.repo.upsert_performance_snapshot(snapshot.to_db_dict())

        logger.info(f"Saved {len(daily_metrics)} daily performance snapshots")

    def analyze_with_claude(
        self,
        data: dict[str, list[dict]],
        days: int = 7,
        high_cost_threshold: float = 50.0,
        low_ctr_threshold: float = 1.0,
        client_context: dict = None,
    ) -> dict[str, Any]:
        """Send data to Claude for analysis.

        Args:
            data: The performance data pulled from Google Ads.
            days: Number of days the data covers.
            high_cost_threshold: EUR threshold for high cost keywords.
            low_ctr_threshold: CTR % threshold for low-performing ads.
            client_context: Business context for dynamic prompts.

        Returns:
            Parsed JSON response from Claude.
        """
        logger.info("Sending data to Claude for analysis...")

        # Format data for the prompt
        prompt = ANALYSIS_PROMPT.format(
            days=days,
            campaign_data=format_campaign_data(data["campaigns"]),
            keyword_data=format_keyword_data(data["keywords"]),
            search_term_data=format_search_term_data(data["search_terms"]),
            ad_data=format_ad_data(data["ads"]),
            converting_search_terms=format_converting_search_terms(data.get("converting_search_terms", [])),
            high_cost_threshold=high_cost_threshold,
            low_ctr_threshold=low_ctr_threshold,
        )

        # Get dynamic system prompt based on client context
        system_prompt = get_system_prompt(client_context)

        # Call Claude
        response = self.claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=8192,  # Increased for larger responses
            system=system_prompt,
            messages=[{"role": "user", "content": prompt}],
        )

        # Extract and parse JSON from response
        response_text = response.content[0].text

        # Find JSON in response (it might be wrapped in markdown code blocks)
        json_start = response_text.find("{")
        json_end = response_text.rfind("}") + 1

        if json_start == -1 or json_end == 0:
            logger.error("No JSON found in Claude response")
            return {"summary": response_text, "recommendations": []}

        json_str = response_text[json_start:json_end]

        # Try to fix common JSON issues
        import re
        # Remove trailing commas before } or ]
        json_str = re.sub(r',\s*}', '}', json_str)
        json_str = re.sub(r',\s*]', ']', json_str)

        try:
            result = json.loads(json_str)
            logger.info(f"Claude generated {len(result.get('recommendations', []))} recommendations")
            return result
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Claude response: {e}")
            # Log a snippet of the problematic area
            error_pos = e.pos if hasattr(e, 'pos') else 0
            logger.error(f"JSON around error: ...{json_str[max(0, error_pos-50):error_pos+50]}...")
            return {"summary": response_text, "recommendations": []}

    def create_recommendations(
        self, analysis_result: dict[str, Any]
    ) -> list[dict]:
        """Convert Claude analysis to Recommendation objects.

        Args:
            analysis_result: Parsed JSON from Claude.

        Returns:
            List of recommendation dicts ready for database insertion.
        """
        recommendations = []

        for rec in analysis_result.get("recommendations", []):
            priority_map = {
                "high": Priority.HIGH,
                "medium": Priority.MEDIUM,
                "low": Priority.LOW,
            }

            recommendation = Recommendation(
                agent=AgentType.GOOGLE_ADS,
                type=rec.get("type", "unknown"),
                priority=priority_map.get(rec.get("priority", "medium"), Priority.MEDIUM),
                title=rec.get("title", "Untitled recommendation"),
                summary=rec.get("summary"),
                details=rec.get("details", {}),
            )
            recommendations.append(recommendation.to_db_dict())

        return recommendations

    async def run(
        self,
        days: int = 7,
        high_cost_threshold: float = 50.0,
        low_ctr_threshold: float = 1.0,
        client_id: str = None,
    ) -> list[dict]:
        """Run the full analysis pipeline.

        Args:
            days: Number of days to analyze.
            high_cost_threshold: EUR threshold for flagging high cost keywords.
            low_ctr_threshold: CTR % threshold for flagging low CTR ads.
            client_id: Optional client ID to scope analysis and get context.

        Returns:
            List of recommendation dicts.
        """
        # Load client context if client_id provided
        client_context = None
        if client_id:
            client = self.repo.get_client(client_id)
            if client:
                client_context = client.get("business_context", {})
                logger.info(f"Using client context for: {client.get('name')}")

        # 1. Pull data from Google Ads
        data = self.pull_data(days)

        # 2. Save daily performance snapshots
        self.save_performance_snapshot(data, days)

        # 3. Analyze with Claude (with client context)
        analysis = self.analyze_with_claude(
            data, days, high_cost_threshold, low_ctr_threshold, client_context
        )

        # 4. Create recommendations (add client_id)
        recommendations = self.create_recommendations(analysis)

        # Add client_id to all recommendations
        if client_id:
            for rec in recommendations:
                rec["client_id"] = client_id

        return recommendations
