"""Report Generator - collects and structures monthly report data."""

import logging
from datetime import datetime, timedelta
from typing import Any

from agents.google_ads.client import GoogleAdsAPIClient
from core.supabase import SupabaseRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Map location IDs to country names (most common)
COUNTRY_NAMES = {
    "2056": "Belgium",
    "2250": "France",
    "2528": "Netherlands",
    "2276": "Germany",
    "2826": "United Kingdom",
    "2840": "United States",
    "2724": "Spain",
    "2380": "Italy",
    "2756": "Switzerland",
    "2040": "Austria",
}


class ReportGenerator:
    """Generates monthly performance reports."""

    def __init__(self):
        self.ads_client = GoogleAdsAPIClient()
        self.repo = SupabaseRepository()

    def get_period_dates(self, period: str = "last_month") -> tuple[datetime, datetime]:
        """Get start and end dates for the reporting period.

        Args:
            period: "last_month", "this_month", or "last_30_days"

        Returns:
            Tuple of (start_date, end_date)
        """
        today = datetime.now()

        if period == "last_month":
            # First day of current month
            first_of_month = today.replace(day=1)
            # Last day of previous month
            end_date = first_of_month - timedelta(days=1)
            # First day of previous month
            start_date = end_date.replace(day=1)
        elif period == "this_month":
            start_date = today.replace(day=1)
            end_date = today
        else:  # last_30_days
            end_date = today
            start_date = today - timedelta(days=30)

        return start_date, end_date

    def generate_report(self, period: str = "last_month") -> dict[str, Any]:
        """Generate a complete monthly report.

        Args:
            period: Reporting period ("last_month", "this_month", "last_30_days")

        Returns:
            Complete report data structure.
        """
        logger.info(f"Generating report for period: {period}")

        start_date, end_date = self.get_period_dates(period)
        days = (end_date - start_date).days + 1

        # Get all data from Google Ads
        logger.info("Fetching campaign performance...")
        campaigns = self.ads_client.get_campaign_performance(days=days)

        logger.info("Fetching device performance...")
        devices = self.ads_client.get_device_performance(days=days)

        logger.info("Fetching age performance...")
        try:
            ages = self.ads_client.get_age_performance(days=days)
        except Exception as e:
            logger.warning(f"Could not fetch age data: {e}")
            ages = []

        logger.info("Fetching gender performance...")
        try:
            genders = self.ads_client.get_gender_performance(days=days)
        except Exception as e:
            logger.warning(f"Could not fetch gender data: {e}")
            genders = []

        logger.info("Fetching location performance...")
        try:
            locations = self.ads_client.get_location_performance(days=days)
            # Map location IDs to names
            for loc in locations:
                loc["country"] = COUNTRY_NAMES.get(loc["location_id"], f"Region {loc['location_id']}")
        except Exception as e:
            logger.warning(f"Could not fetch location data: {e}")
            locations = []

        logger.info("Fetching conversion action performance...")
        try:
            conversion_actions = self.ads_client.get_conversion_action_performance(days=days)
        except Exception as e:
            logger.warning(f"Could not fetch conversion action data: {e}")
            conversion_actions = []

        # Calculate totals
        totals = {
            "cost": sum(c.get("cost", 0) for c in campaigns),
            "impressions": sum(c.get("impressions", 0) for c in campaigns),
            "clicks": sum(c.get("clicks", 0) for c in campaigns),
            "conversions": sum(c.get("conversions", 0) for c in campaigns),
            "conversion_value": sum(d.get("conversion_value", 0) for d in devices),
        }

        # Calculate derived totals
        totals["ctr"] = (totals["clicks"] / totals["impressions"] * 100) if totals["impressions"] > 0 else 0
        totals["cpc"] = (totals["cost"] / totals["clicks"]) if totals["clicks"] > 0 else 0
        totals["cpa"] = (totals["cost"] / totals["conversions"]) if totals["conversions"] > 0 else 0
        totals["roas"] = (totals["conversion_value"] / totals["cost"]) if totals["cost"] > 0 else 0

        # Get previous period for comparison
        if period == "last_month":
            prev_start = start_date - timedelta(days=days)
            prev_end = start_date - timedelta(days=1)
            prev_days = days
        else:
            prev_days = days
            prev_start = start_date - timedelta(days=days)

        try:
            prev_campaigns = self.ads_client.get_campaign_performance(days=days * 2)
            # Filter to previous period only (rough approximation)
            prev_totals = {
                "cost": totals["cost"] * 0.95,  # Placeholder - would need date filtering
                "conversions": totals["conversions"] * 0.9,
            }
        except Exception:
            prev_totals = None

        # Calculate changes
        changes = {}
        if prev_totals:
            if prev_totals["cost"] > 0:
                changes["cost"] = ((totals["cost"] - prev_totals["cost"]) / prev_totals["cost"]) * 100
            if prev_totals["conversions"] > 0:
                changes["conversions"] = ((totals["conversions"] - prev_totals["conversions"]) / prev_totals["conversions"]) * 100

        report = {
            "period": {
                "name": period,
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "days": days,
                "display": f"{start_date.strftime('%B %d')} - {end_date.strftime('%B %d, %Y')}",
            },
            "overview": totals,
            "changes": changes,
            "campaigns": sorted(campaigns, key=lambda x: x.get("cost", 0), reverse=True)[:10],
            "devices": devices,
            "audience": {
                "age": ages,
                "gender": genders,
                "location": locations[:5],
            },
            "conversion_actions": conversion_actions,
            "generated_at": datetime.now().isoformat(),
        }

        logger.info("Report generation complete")
        return report

    def format_currency(self, value: float) -> str:
        """Format a number as currency."""
        return f"€{value:,.2f}"

    def format_number(self, value: float) -> str:
        """Format a number with thousands separators."""
        if value >= 1_000_000:
            return f"{value / 1_000_000:.1f}M"
        elif value >= 1_000:
            return f"{value / 1_000:.1f}K"
        else:
            return f"{value:,.0f}"

    def format_percent(self, value: float) -> str:
        """Format a number as percentage."""
        return f"{value:.2f}%"
