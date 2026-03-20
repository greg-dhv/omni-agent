"""Google Ads Executor - executes approved recommendations."""

import logging
from datetime import datetime
from typing import Any

from .client import GoogleAdsAPIClient
from core.models import Action, AgentType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GoogleAdsExecutor:
    """Executes approved Google Ads recommendations."""

    def __init__(self, config_path: str = "config/google-ads.yaml"):
        self.ads_client = GoogleAdsAPIClient(config_path)

    def execute(self, recommendation: dict) -> dict:
        """Execute a single recommendation.

        Args:
            recommendation: The approved recommendation to execute.

        Returns:
            Action dict recording what was done.
        """
        rec_type = recommendation.get("type")
        details = recommendation.get("details", {})

        logger.info(f"Executing recommendation: {rec_type}")

        action = Action(
            recommendation_id=recommendation.get("id"),
            agent=AgentType.GOOGLE_ADS,
            action_type=rec_type,
            title=recommendation.get("title"),
            metadata=details,
        )

        try:
            if rec_type == "pause_keyword":
                success = self._pause_keyword(details)
                action.description = f"Paused keyword '{details.get('keyword_text')}'"
                action.impact = f"Saved €{details.get('cost', 0):.2f}/week potential waste"

            elif rec_type == "add_negative":
                success = self._add_negative_keyword(details)
                action.description = f"Added negative keyword '{details.get('search_term')}'"
                action.impact = "Reduced irrelevant traffic"

            elif rec_type == "add_keyword":
                success = self._add_keyword(details)
                keyword = details.get('search_term') or details.get('keyword_text')
                action.description = f"Added keyword '{keyword}' to ad group '{details.get('ad_group_name')}'"
                action.impact = "Expanded keyword coverage for converting search terms"

            elif rec_type == "pause_ad":
                success = self._pause_ad(details)
                action.description = f"Paused underperforming ad in '{details.get('ad_group_name')}'"
                action.impact = "Improved overall ad group CTR"

            elif rec_type == "improve_ad":
                # RSA headlines/descriptions cannot be modified via API
                # This is an informational recommendation for manual action
                success = True
                action.description = f"Manual action required: Improve ad in '{details.get('campaign_name')}'"
                action.impact = f"Add suggested headlines/descriptions to improve ad strength from {details.get('ad_strength', 'UNKNOWN')}"
                action.result = "success"

            elif rec_type == "adjust_budget":
                # Budget adjustments are typically manual for now
                success = False
                action.description = "Budget adjustment flagged for manual review"
                action.result = "partial"

            elif rec_type == "flag_anomaly":
                # Anomalies are informational, no action needed
                success = True
                action.description = recommendation.get("title")
                action.result = "success"

            else:
                logger.warning(f"Unknown recommendation type: {rec_type}")
                success = False
                action.description = f"Unknown action type: {rec_type}"
                action.result = "failed"

            if rec_type not in ("adjust_budget", "flag_anomaly"):
                action.result = "success" if success else "failed"

            if not success and rec_type not in ("flag_anomaly",):
                action.error_message = "API call failed"

        except Exception as e:
            logger.error(f"Error executing {rec_type}: {e}")
            action.result = "failed"
            action.error_message = str(e)

        action.executed_at = datetime.utcnow()
        return action.to_db_dict()

    def _pause_keyword(self, details: dict) -> bool:
        """Pause a keyword."""
        ad_group_id = details.get("ad_group_id")
        keyword_id = details.get("keyword_id")

        if not ad_group_id or not keyword_id:
            logger.error("Missing ad_group_id or keyword_id")
            return False

        return self.ads_client.pause_keyword(ad_group_id, keyword_id)

    def _add_negative_keyword(self, details: dict) -> bool:
        """Add a negative keyword."""
        campaign_id = details.get("campaign_id")
        search_term = details.get("search_term") or details.get("keyword_text")
        match_type = details.get("suggested_action", "add_negative_exact")

        if not campaign_id or not search_term:
            logger.error("Missing campaign_id or search_term")
            return False

        # Determine match type
        if "phrase" in match_type.lower():
            match = "PHRASE"
        elif "broad" in match_type.lower():
            match = "BROAD"
        else:
            match = "EXACT"

        return self.ads_client.add_negative_keyword(campaign_id, search_term, match)

    def _pause_ad(self, details: dict) -> bool:
        """Pause an ad."""
        ad_group_id = details.get("ad_group_id")
        ad_id = details.get("ad_id")

        if not ad_group_id or not ad_id:
            logger.error("Missing ad_group_id or ad_id")
            return False

        return self.ads_client.pause_ad(ad_group_id, ad_id)

    def _add_keyword(self, details: dict) -> bool:
        """Add a keyword to an ad group."""
        ad_group_id = details.get("ad_group_id")
        keyword_text = details.get("search_term") or details.get("keyword_text")
        match_type = details.get("match_type", "BROAD")

        if not ad_group_id or not keyword_text:
            logger.error("Missing ad_group_id or keyword_text")
            return False

        # Normalize match type
        if isinstance(match_type, str):
            match_type = match_type.upper()
            if match_type not in ("EXACT", "PHRASE", "BROAD"):
                match_type = "BROAD"

        logger.info(f"Adding keyword '{keyword_text}' ({match_type}) to ad group {ad_group_id}")

        return self.ads_client.add_keyword(ad_group_id, keyword_text, match_type)

    def _improve_ad(self, details: dict) -> bool:
        """Improve a responsive search ad by adding headlines/descriptions."""
        ad_group_id = details.get("ad_group_id")
        ad_id = details.get("ad_id")
        current_headlines = details.get("current_headlines", [])
        suggested_headlines = details.get("suggested_headlines", [])
        current_descriptions = details.get("current_descriptions", [])
        suggested_descriptions = details.get("suggested_descriptions", [])

        if not ad_group_id or not ad_id:
            logger.error("Missing ad_group_id or ad_id")
            return False

        if not suggested_headlines and not suggested_descriptions:
            logger.error("No suggested headlines or descriptions to add")
            return False

        logger.info(f"Improving ad {ad_id}: adding {len(suggested_headlines)} headlines, {len(suggested_descriptions)} descriptions")

        return self.ads_client.update_responsive_search_ad(
            ad_group_id=ad_group_id,
            ad_id=ad_id,
            current_headlines=current_headlines,
            new_headlines=suggested_headlines,
            current_descriptions=current_descriptions,
            new_descriptions=suggested_descriptions,
        )
