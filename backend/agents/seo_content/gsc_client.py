"""Google Search Console API client."""

import os
from datetime import datetime, timedelta
from typing import Any

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GSCClient:
    """Client for Google Search Console API."""

    def __init__(self, site_url: str = None, credentials: dict = None):
        """Initialize GSC client.

        Args:
            site_url: The site URL in GSC (e.g., 'sc-domain:example.com' or 'https://example.com/')
            credentials: OAuth credentials dict with refresh_token, client_id, client_secret
        """
        self.site_url = site_url or os.environ.get("GSC_SITE_URL")
        self.service = self._build_service(credentials)

    def _build_service(self, credentials: dict = None):
        """Build the GSC service using OAuth credentials."""
        if credentials:
            creds = Credentials(
                token=None,
                refresh_token=credentials.get("refresh_token"),
                client_id=credentials.get("client_id"),
                client_secret=credentials.get("client_secret"),
                token_uri="https://oauth2.googleapis.com/token",
            )
        else:
            # Load from environment
            creds = Credentials(
                token=None,
                refresh_token=os.environ.get("GSC_REFRESH_TOKEN"),
                client_id=os.environ.get("GOOGLE_CLIENT_ID"),
                client_secret=os.environ.get("GOOGLE_CLIENT_SECRET"),
                token_uri="https://oauth2.googleapis.com/token",
            )

        return build("searchconsole", "v1", credentials=creds)

    def get_search_analytics(
        self,
        days: int = 28,
        row_limit: int = 500,
        dimensions: list[str] = None,
    ) -> list[dict[str, Any]]:
        """Get search analytics data from GSC.

        Args:
            days: Number of days to look back (max 16 months).
            row_limit: Maximum rows to return (max 25000).
            dimensions: Dimensions to group by (default: ['query', 'page']).

        Returns:
            List of search analytics rows with clicks, impressions, ctr, position.
        """
        if dimensions is None:
            dimensions = ["query"]

        end_date = datetime.now() - timedelta(days=3)  # GSC data has 3-day delay
        start_date = end_date - timedelta(days=days)

        request = {
            "startDate": start_date.strftime("%Y-%m-%d"),
            "endDate": end_date.strftime("%Y-%m-%d"),
            "dimensions": dimensions,
            "rowLimit": row_limit,
            "dataState": "final",
        }

        try:
            response = self.service.searchanalytics().query(
                siteUrl=self.site_url, body=request
            ).execute()

            rows = response.get("rows", [])
            results = []

            for row in rows:
                result = {
                    "clicks": row.get("clicks", 0),
                    "impressions": row.get("impressions", 0),
                    "ctr": row.get("ctr", 0),
                    "position": row.get("position", 0),
                }
                # Add dimension values
                for i, dim in enumerate(dimensions):
                    result[dim] = row.get("keys", [])[i] if i < len(row.get("keys", [])) else ""

                results.append(result)

            return results

        except HttpError as e:
            print(f"GSC API error: {e}")
            raise

    def get_keyword_opportunities(self, days: int = 28) -> dict[str, list[dict]]:
        """Identify keyword opportunities from GSC data.

        Returns keywords grouped by opportunity type:
        - quick_wins: Ranking 4-10 with decent impressions (close to top 3)
        - low_hanging_fruit: Ranking 11-20 with high impressions (close to page 1)
        - ctr_opportunities: High impressions but low CTR (needs better snippet)
        - striking_distance: Ranking 21-30 (page 2-3, potential to reach page 1)

        Args:
            days: Number of days to analyze.

        Returns:
            Dict with categorized keyword opportunities.
        """
        data = self.get_search_analytics(days=days, row_limit=1000)

        opportunities = {
            "quick_wins": [],
            "low_hanging_fruit": [],
            "ctr_opportunities": [],
            "striking_distance": [],
        }

        for row in data:
            query = row.get("query", "")
            position = row.get("position", 100)
            impressions = row.get("impressions", 0)
            ctr = row.get("ctr", 0)
            clicks = row.get("clicks", 0)

            # Skip branded queries (you might want to customize this)
            if len(query) < 3:
                continue

            keyword_data = {
                "keyword": query,
                "position": round(position, 1),
                "impressions": impressions,
                "clicks": clicks,
                "ctr": round(ctr * 100, 2),  # Convert to percentage
            }

            # Quick wins: Position 4-10, decent impressions
            if 4 <= position <= 10 and impressions >= 50:
                keyword_data["opportunity"] = "Optimize to reach top 3"
                keyword_data["priority"] = "high"
                opportunities["quick_wins"].append(keyword_data)

            # Low hanging fruit: Position 11-20, high impressions
            elif 11 <= position <= 20 and impressions >= 100:
                keyword_data["opportunity"] = "Push to page 1"
                keyword_data["priority"] = "high"
                opportunities["low_hanging_fruit"].append(keyword_data)

            # CTR opportunities: Good position but poor CTR
            elif position <= 10 and impressions >= 100 and ctr < 0.03:
                keyword_data["opportunity"] = "Improve title/meta description"
                keyword_data["priority"] = "medium"
                opportunities["ctr_opportunities"].append(keyword_data)

            # Striking distance: Position 21-30 with impressions
            elif 21 <= position <= 30 and impressions >= 50:
                keyword_data["opportunity"] = "Create dedicated content"
                keyword_data["priority"] = "medium"
                opportunities["striking_distance"].append(keyword_data)

        # Sort each category by impressions (highest first)
        for category in opportunities:
            opportunities[category].sort(key=lambda x: x["impressions"], reverse=True)
            # Limit to top 10 per category
            opportunities[category] = opportunities[category][:10]

        return opportunities

    def get_top_pages(self, days: int = 28, limit: int = 20) -> list[dict]:
        """Get top performing pages.

        Args:
            days: Number of days to analyze.
            limit: Number of pages to return.

        Returns:
            List of top pages with their metrics.
        """
        data = self.get_search_analytics(
            days=days,
            row_limit=limit,
            dimensions=["page"],
        )

        return sorted(data, key=lambda x: x.get("clicks", 0), reverse=True)

    def get_query_page_data(self, days: int = 28, limit: int = 500) -> list[dict]:
        """Get query + page combined data for content gap analysis.

        Args:
            days: Number of days to analyze.
            limit: Number of rows to return.

        Returns:
            List of query-page combinations with metrics.
        """
        return self.get_search_analytics(
            days=days,
            row_limit=limit,
            dimensions=["query", "page"],
        )
