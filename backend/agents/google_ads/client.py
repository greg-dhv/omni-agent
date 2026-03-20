"""Google Ads API client wrapper."""

import os
from datetime import datetime, timedelta
from typing import Any
import yaml

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException


class GoogleAdsAPIClient:
    """Wrapper for Google Ads API operations."""

    def __init__(
        self,
        config_path: str = None,
        client_credentials: dict = None,
    ):
        """Initialize the Google Ads client.

        Args:
            config_path: Path to google-ads.yaml (legacy, for single client).
            client_credentials: Dict with credentials from database for multi-client:
                - google_ads_customer_id
                - google_ads_login_customer_id
                - google_ads_refresh_token
        """
        if client_credentials:
            # Load from database credentials (multi-client mode)
            self.client = self._create_client_from_credentials(client_credentials)
            self.customer_id = client_credentials.get("google_ads_customer_id", "").replace("-", "")
        elif config_path:
            # Load from YAML file (legacy single-client mode)
            self.client = GoogleAdsClient.load_from_storage(config_path)
            self.customer_id = os.environ.get("GOOGLE_ADS_CUSTOMER_ID", "").replace("-", "")
        else:
            # Default to config file
            self.client = GoogleAdsClient.load_from_storage("config/google-ads.yaml")
            self.customer_id = os.environ.get("GOOGLE_ADS_CUSTOMER_ID", "").replace("-", "")

    def _create_client_from_credentials(self, credentials: dict) -> GoogleAdsClient:
        """Create a GoogleAdsClient from database credentials."""
        # Load shared credentials from environment/config
        # (developer_token and client_id/secret are shared across all clients)
        with open("config/google-ads.yaml", "r") as f:
            base_config = yaml.safe_load(f)

        config = {
            "developer_token": base_config.get("developer_token"),
            "client_id": base_config.get("client_id"),
            "client_secret": base_config.get("client_secret"),
            "refresh_token": credentials.get("google_ads_refresh_token"),
            "login_customer_id": credentials.get("google_ads_login_customer_id"),
            "use_proto_plus": True,
        }

        return GoogleAdsClient.load_from_dict(config)

    @classmethod
    def for_client(cls, client_data: dict) -> "GoogleAdsAPIClient":
        """Factory method to create a client for a specific business.

        Args:
            client_data: Client record from Supabase with Google Ads credentials.

        Returns:
            GoogleAdsAPIClient configured for the client.
        """
        return cls(client_credentials={
            "google_ads_customer_id": client_data.get("google_ads_customer_id"),
            "google_ads_login_customer_id": client_data.get("google_ads_login_customer_id"),
            "google_ads_refresh_token": client_data.get("google_ads_refresh_token"),
        })

    def _get_service(self, service_name: str):
        """Get a Google Ads service."""
        return self.client.get_service(service_name)

    def get_campaign_performance(
        self, days: int = 7
    ) -> list[dict[str, Any]]:
        """Get campaign performance data for the last N days.

        Returns:
            List of campaign performance records.
        """
        ga_service = self._get_service("GoogleAdsService")

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        query = f"""
            SELECT
                campaign.id,
                campaign.name,
                campaign.status,
                campaign.advertising_channel_type,
                metrics.cost_micros,
                metrics.clicks,
                metrics.impressions,
                metrics.conversions,
                metrics.ctr,
                metrics.average_cpc,
                metrics.cost_per_conversion
            FROM campaign
            WHERE segments.date BETWEEN '{start_date.strftime('%Y-%m-%d')}' AND '{end_date.strftime('%Y-%m-%d')}'
            AND campaign.status = 'ENABLED'
            ORDER BY metrics.cost_micros DESC
        """

        results = []
        try:
            response = ga_service.search(customer_id=self.customer_id, query=query)
            for row in response:
                results.append({
                    "campaign_id": str(row.campaign.id),
                    "campaign_name": row.campaign.name,
                    "status": row.campaign.status.name,
                    "channel_type": row.campaign.advertising_channel_type.name,
                    "cost": row.metrics.cost_micros / 1_000_000,  # Convert to EUR
                    "clicks": row.metrics.clicks,
                    "impressions": row.metrics.impressions,
                    "conversions": row.metrics.conversions,
                    "ctr": row.metrics.ctr * 100,  # Convert to percentage
                    "avg_cpc": row.metrics.average_cpc / 1_000_000,
                    "cost_per_conversion": row.metrics.cost_per_conversion / 1_000_000 if row.metrics.conversions > 0 else None,
                })
        except GoogleAdsException as e:
            print(f"Google Ads API error: {e}")
            raise

        return results

    def get_keyword_performance(self, days: int = 7) -> list[dict[str, Any]]:
        """Get keyword performance data for the last N days.

        Returns:
            List of keyword performance records.
        """
        ga_service = self._get_service("GoogleAdsService")

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        query = f"""
            SELECT
                campaign.id,
                campaign.name,
                ad_group.id,
                ad_group.name,
                ad_group_criterion.criterion_id,
                ad_group_criterion.keyword.text,
                ad_group_criterion.keyword.match_type,
                ad_group_criterion.status,
                metrics.cost_micros,
                metrics.clicks,
                metrics.impressions,
                metrics.conversions,
                metrics.ctr,
                metrics.average_cpc,
                metrics.cost_per_conversion
            FROM keyword_view
            WHERE segments.date BETWEEN '{start_date.strftime('%Y-%m-%d')}' AND '{end_date.strftime('%Y-%m-%d')}'
            AND ad_group_criterion.status = 'ENABLED'
            AND campaign.status = 'ENABLED'
            ORDER BY metrics.cost_micros DESC
            LIMIT 500
        """

        results = []
        try:
            response = ga_service.search(customer_id=self.customer_id, query=query)
            for row in response:
                results.append({
                    "campaign_id": str(row.campaign.id),
                    "campaign_name": row.campaign.name,
                    "ad_group_id": str(row.ad_group.id),
                    "ad_group_name": row.ad_group.name,
                    "keyword_id": str(row.ad_group_criterion.criterion_id),
                    "keyword_text": row.ad_group_criterion.keyword.text,
                    "match_type": row.ad_group_criterion.keyword.match_type.name,
                    "status": row.ad_group_criterion.status.name,
                    "cost": row.metrics.cost_micros / 1_000_000,
                    "clicks": row.metrics.clicks,
                    "impressions": row.metrics.impressions,
                    "conversions": row.metrics.conversions,
                    "ctr": row.metrics.ctr * 100,
                    "avg_cpc": row.metrics.average_cpc / 1_000_000,
                    "cost_per_conversion": row.metrics.cost_per_conversion / 1_000_000 if row.metrics.conversions > 0 else None,
                })
        except GoogleAdsException as e:
            print(f"Google Ads API error: {e}")
            raise

        return results

    def get_search_terms(self, days: int = 7) -> list[dict[str, Any]]:
        """Get search term performance data.

        Returns:
            List of search term records.
        """
        ga_service = self._get_service("GoogleAdsService")

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        query = f"""
            SELECT
                campaign.id,
                campaign.name,
                ad_group.id,
                ad_group.name,
                search_term_view.search_term,
                metrics.cost_micros,
                metrics.clicks,
                metrics.impressions,
                metrics.conversions
            FROM search_term_view
            WHERE segments.date BETWEEN '{start_date.strftime('%Y-%m-%d')}' AND '{end_date.strftime('%Y-%m-%d')}'
            AND campaign.status = 'ENABLED'
            ORDER BY metrics.cost_micros DESC
            LIMIT 500
        """

        results = []
        try:
            response = ga_service.search(customer_id=self.customer_id, query=query)
            for row in response:
                results.append({
                    "campaign_id": str(row.campaign.id),
                    "campaign_name": row.campaign.name,
                    "ad_group_id": str(row.ad_group.id),
                    "ad_group_name": row.ad_group.name,
                    "search_term": row.search_term_view.search_term,
                    "cost": row.metrics.cost_micros / 1_000_000,
                    "clicks": row.metrics.clicks,
                    "impressions": row.metrics.impressions,
                    "conversions": row.metrics.conversions,
                })
        except GoogleAdsException as e:
            print(f"Google Ads API error: {e}")
            raise

        return results

    def get_ad_performance(self, days: int = 7) -> list[dict[str, Any]]:
        """Get ad performance data with ad strength.

        Returns:
            List of ad performance records including ad strength.
        """
        ga_service = self._get_service("GoogleAdsService")

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        query = f"""
            SELECT
                campaign.id,
                campaign.name,
                ad_group.id,
                ad_group.name,
                ad_group_ad.ad.id,
                ad_group_ad.ad.responsive_search_ad.headlines,
                ad_group_ad.ad.responsive_search_ad.descriptions,
                ad_group_ad.ad.responsive_search_ad.path1,
                ad_group_ad.ad.responsive_search_ad.path2,
                ad_group_ad.ad_strength,
                ad_group_ad.status,
                metrics.cost_micros,
                metrics.clicks,
                metrics.impressions,
                metrics.conversions,
                metrics.ctr
            FROM ad_group_ad
            WHERE segments.date BETWEEN '{start_date.strftime('%Y-%m-%d')}' AND '{end_date.strftime('%Y-%m-%d')}'
            AND ad_group_ad.status = 'ENABLED'
            AND campaign.status = 'ENABLED'
            ORDER BY metrics.impressions DESC
            LIMIT 200
        """

        results = []
        try:
            response = ga_service.search(customer_id=self.customer_id, query=query)
            for row in response:
                headlines = []
                descriptions = []
                if row.ad_group_ad.ad.responsive_search_ad:
                    headlines = [h.text for h in row.ad_group_ad.ad.responsive_search_ad.headlines]
                    descriptions = [d.text for d in row.ad_group_ad.ad.responsive_search_ad.descriptions]

                results.append({
                    "campaign_id": str(row.campaign.id),
                    "campaign_name": row.campaign.name,
                    "ad_group_id": str(row.ad_group.id),
                    "ad_group_name": row.ad_group.name,
                    "ad_id": str(row.ad_group_ad.ad.id),
                    "headlines": headlines,
                    "descriptions": descriptions,
                    "ad_strength": row.ad_group_ad.ad_strength.name,  # POOR, AVERAGE, GOOD, EXCELLENT
                    "status": row.ad_group_ad.status.name,
                    "cost": row.metrics.cost_micros / 1_000_000,
                    "clicks": row.metrics.clicks,
                    "impressions": row.metrics.impressions,
                    "conversions": row.metrics.conversions,
                    "ctr": row.metrics.ctr * 100,
                })
        except GoogleAdsException as e:
            print(f"Google Ads API error: {e}")
            raise

        return results

    def get_daily_metrics(self, days: int = 30) -> list[dict[str, Any]]:
        """Get daily aggregate metrics for the last N days.

        Returns data with one row per day for accurate time-range filtering.

        Returns:
            List of daily metrics records.
        """
        ga_service = self._get_service("GoogleAdsService")

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        query = f"""
            SELECT
                segments.date,
                metrics.cost_micros,
                metrics.clicks,
                metrics.impressions,
                metrics.conversions
            FROM campaign
            WHERE segments.date BETWEEN '{start_date.strftime('%Y-%m-%d')}' AND '{end_date.strftime('%Y-%m-%d')}'
        """

        # Aggregate by date
        daily_data = {}
        try:
            response = ga_service.search(customer_id=self.customer_id, query=query)
            for row in response:
                date_str = row.segments.date
                if date_str not in daily_data:
                    daily_data[date_str] = {
                        "date": date_str,
                        "cost": 0,
                        "clicks": 0,
                        "impressions": 0,
                        "conversions": 0,
                    }
                daily_data[date_str]["cost"] += row.metrics.cost_micros / 1_000_000
                daily_data[date_str]["clicks"] += row.metrics.clicks
                daily_data[date_str]["impressions"] += row.metrics.impressions
                daily_data[date_str]["conversions"] += row.metrics.conversions

        except GoogleAdsException as e:
            print(f"Google Ads API error: {e}")
            raise

        # Calculate derived metrics
        results = []
        for date_str, data in sorted(daily_data.items()):
            data["ctr"] = (data["clicks"] / data["impressions"] * 100) if data["impressions"] > 0 else 0
            data["cpc"] = (data["cost"] / data["clicks"]) if data["clicks"] > 0 else 0
            results.append(data)

        return results

    def get_conversion_action_performance(self, days: int = 30) -> list[dict[str, Any]]:
        """Get performance breakdown by conversion action (FTD, signup, purchase, etc).

        Returns:
            List of conversion action performance records.
        """
        ga_service = self._get_service("GoogleAdsService")

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        query = f"""
            SELECT
                segments.conversion_action_name,
                segments.conversion_action_category,
                metrics.conversions,
                metrics.conversions_value,
                metrics.all_conversions,
                metrics.all_conversions_value
            FROM campaign
            WHERE segments.date BETWEEN '{start_date.strftime('%Y-%m-%d')}' AND '{end_date.strftime('%Y-%m-%d')}'
        """

        conversion_data = {}
        try:
            response = ga_service.search(customer_id=self.customer_id, query=query)
            for row in response:
                action_name = row.segments.conversion_action_name
                if not action_name:
                    continue

                if action_name not in conversion_data:
                    conversion_data[action_name] = {
                        "conversion_action": action_name,
                        "category": row.segments.conversion_action_category.name if row.segments.conversion_action_category else "OTHER",
                        "conversions": 0,
                        "conversion_value": 0,
                        "all_conversions": 0,
                        "all_conversions_value": 0,
                    }
                conversion_data[action_name]["conversions"] += row.metrics.conversions
                conversion_data[action_name]["conversion_value"] += row.metrics.conversions_value
                conversion_data[action_name]["all_conversions"] += row.metrics.all_conversions
                conversion_data[action_name]["all_conversions_value"] += row.metrics.all_conversions_value

        except GoogleAdsException as e:
            print(f"Google Ads API error: {e}")
            raise

        # Sort by conversions descending
        results = sorted(conversion_data.values(), key=lambda x: x["conversions"], reverse=True)
        return results

    def get_converting_search_terms(self, days: int = 30, min_conversions: float = 1) -> list[dict[str, Any]]:
        """Get search terms with conversions that aren't yet keywords.

        Returns:
            List of high-converting search terms for keyword discovery.
        """
        ga_service = self._get_service("GoogleAdsService")

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        query = f"""
            SELECT
                campaign.id,
                campaign.name,
                ad_group.id,
                ad_group.name,
                search_term_view.search_term,
                search_term_view.status,
                metrics.cost_micros,
                metrics.clicks,
                metrics.impressions,
                metrics.conversions,
                metrics.conversions_value
            FROM search_term_view
            WHERE segments.date BETWEEN '{start_date.strftime('%Y-%m-%d')}' AND '{end_date.strftime('%Y-%m-%d')}'
            AND campaign.status = 'ENABLED'
            AND metrics.conversions > 0
            ORDER BY metrics.conversions DESC
            LIMIT 100
        """

        results = []
        try:
            response = ga_service.search(customer_id=self.customer_id, query=query)
            for row in response:
                results.append({
                    "campaign_id": str(row.campaign.id),
                    "campaign_name": row.campaign.name,
                    "ad_group_id": str(row.ad_group.id),
                    "ad_group_name": row.ad_group.name,
                    "search_term": row.search_term_view.search_term,
                    "status": row.search_term_view.status.name,  # ADDED, EXCLUDED, NONE
                    "cost": row.metrics.cost_micros / 1_000_000,
                    "clicks": row.metrics.clicks,
                    "impressions": row.metrics.impressions,
                    "conversions": row.metrics.conversions,
                    "conversion_value": row.metrics.conversions_value,
                    "cpa": (row.metrics.cost_micros / 1_000_000) / row.metrics.conversions if row.metrics.conversions > 0 else None,
                })
        except GoogleAdsException as e:
            print(f"Google Ads API error: {e}")
            raise

        return results

    # ==================== Mutation Methods ====================

    def add_keyword(
        self,
        ad_group_id: str,
        keyword_text: str,
        match_type: str = "BROAD",
    ) -> bool:
        """Add a keyword to an ad group.

        Args:
            ad_group_id: The ad group ID.
            keyword_text: The keyword text to add.
            match_type: EXACT, PHRASE, or BROAD.

        Returns:
            True if successful.
        """
        ad_group_criterion_service = self._get_service("AdGroupCriterionService")
        ga_service = self._get_service("GoogleAdsService")

        ad_group_resource = ga_service.ad_group_path(self.customer_id, ad_group_id)

        operation = self.client.get_type("AdGroupCriterionOperation")
        criterion = operation.create
        criterion.ad_group = ad_group_resource
        criterion.status = self.client.enums.AdGroupCriterionStatusEnum.ENABLED
        criterion.keyword.text = keyword_text
        criterion.keyword.match_type = self.client.enums.KeywordMatchTypeEnum[match_type]

        try:
            response = ad_group_criterion_service.mutate_ad_group_criteria(
                customer_id=self.customer_id,
                operations=[operation],
            )
            print(f"Added keyword: {response.results[0].resource_name}")
            return True
        except GoogleAdsException as e:
            print(f"Failed to add keyword: {e}")
            for error in e.failure.errors:
                print(f"  Error: {error.message}")
            return False

    def pause_keyword(self, ad_group_id: str, criterion_id: str) -> bool:
        """Pause a keyword.

        Args:
            ad_group_id: The ad group ID.
            criterion_id: The keyword criterion ID.

        Returns:
            True if successful.
        """
        ad_group_criterion_service = self._get_service("AdGroupCriterionService")

        resource_name = ad_group_criterion_service.ad_group_criterion_path(
            self.customer_id, ad_group_id, criterion_id
        )

        operation = self.client.get_type("AdGroupCriterionOperation")
        criterion = operation.update
        criterion.resource_name = resource_name
        criterion.status = self.client.enums.AdGroupCriterionStatusEnum.PAUSED

        field_mask = self.client.get_type("FieldMask")
        field_mask.paths.append("status")
        operation.update_mask.CopyFrom(field_mask)

        try:
            response = ad_group_criterion_service.mutate_ad_group_criteria(
                customer_id=self.customer_id,
                operations=[operation],
            )
            return True
        except GoogleAdsException as e:
            print(f"Failed to pause keyword: {e}")
            return False

    def add_negative_keyword(
        self, campaign_id: str, keyword_text: str, match_type: str = "EXACT"
    ) -> bool:
        """Add a negative keyword to a campaign.

        Args:
            campaign_id: The campaign ID.
            keyword_text: The keyword text.
            match_type: EXACT, PHRASE, or BROAD.

        Returns:
            True if successful.
        """
        campaign_criterion_service = self._get_service("CampaignCriterionService")

        campaign_resource = self._get_service("GoogleAdsService").campaign_path(
            self.customer_id, campaign_id
        )

        operation = self.client.get_type("CampaignCriterionOperation")
        criterion = operation.create
        criterion.campaign = campaign_resource
        criterion.negative = True
        criterion.keyword.text = keyword_text
        criterion.keyword.match_type = self.client.enums.KeywordMatchTypeEnum[match_type]

        try:
            response = campaign_criterion_service.mutate_campaign_criteria(
                customer_id=self.customer_id,
                operations=[operation],
            )
            return True
        except GoogleAdsException as e:
            print(f"Failed to add negative keyword: {e}")
            return False

    def pause_ad(self, ad_group_id: str, ad_id: str) -> bool:
        """Pause an ad.

        Args:
            ad_group_id: The ad group ID.
            ad_id: The ad ID.

        Returns:
            True if successful.
        """
        ad_group_ad_service = self._get_service("AdGroupAdService")

        resource_name = ad_group_ad_service.ad_group_ad_path(
            self.customer_id, ad_group_id, ad_id
        )

        operation = self.client.get_type("AdGroupAdOperation")
        ad_group_ad = operation.update
        ad_group_ad.resource_name = resource_name
        ad_group_ad.status = self.client.enums.AdGroupAdStatusEnum.PAUSED

        field_mask = self.client.get_type("FieldMask")
        field_mask.paths.append("status")
        operation.update_mask.CopyFrom(field_mask)

        try:
            response = ad_group_ad_service.mutate_ad_group_ads(
                customer_id=self.customer_id,
                operations=[operation],
            )
            return True
        except GoogleAdsException as e:
            print(f"Failed to pause ad: {e}")
            return False

    def get_device_performance(self, days: int = 30) -> list[dict[str, Any]]:
        """Get performance breakdown by device type.

        Returns:
            List of device performance records.
        """
        ga_service = self._get_service("GoogleAdsService")

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        query = f"""
            SELECT
                segments.device,
                metrics.cost_micros,
                metrics.clicks,
                metrics.impressions,
                metrics.conversions,
                metrics.conversions_value
            FROM campaign
            WHERE segments.date BETWEEN '{start_date.strftime('%Y-%m-%d')}' AND '{end_date.strftime('%Y-%m-%d')}'
        """

        device_data = {}
        try:
            response = ga_service.search(customer_id=self.customer_id, query=query)
            for row in response:
                device = row.segments.device.name
                if device not in device_data:
                    device_data[device] = {
                        "device": device,
                        "cost": 0,
                        "clicks": 0,
                        "impressions": 0,
                        "conversions": 0,
                        "conversion_value": 0,
                    }
                device_data[device]["cost"] += row.metrics.cost_micros / 1_000_000
                device_data[device]["clicks"] += row.metrics.clicks
                device_data[device]["impressions"] += row.metrics.impressions
                device_data[device]["conversions"] += row.metrics.conversions
                device_data[device]["conversion_value"] += row.metrics.conversions_value

        except GoogleAdsException as e:
            print(f"Google Ads API error: {e}")
            raise

        # Calculate derived metrics
        results = []
        for device, data in device_data.items():
            data["ctr"] = (data["clicks"] / data["impressions"] * 100) if data["impressions"] > 0 else 0
            data["cpc"] = (data["cost"] / data["clicks"]) if data["clicks"] > 0 else 0
            data["conv_rate"] = (data["conversions"] / data["clicks"] * 100) if data["clicks"] > 0 else 0
            results.append(data)

        # Sort by cost descending
        return sorted(results, key=lambda x: x["cost"], reverse=True)

    def get_age_performance(self, days: int = 30) -> list[dict[str, Any]]:
        """Get performance breakdown by age range.

        Returns:
            List of age range performance records.
        """
        ga_service = self._get_service("GoogleAdsService")

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        query = f"""
            SELECT
                ad_group_criterion.age_range.type,
                metrics.cost_micros,
                metrics.clicks,
                metrics.impressions,
                metrics.conversions,
                metrics.conversions_value
            FROM age_range_view
            WHERE segments.date BETWEEN '{start_date.strftime('%Y-%m-%d')}' AND '{end_date.strftime('%Y-%m-%d')}'
        """

        age_data = {}
        try:
            response = ga_service.search(customer_id=self.customer_id, query=query)
            for row in response:
                age_range = row.ad_group_criterion.age_range.type.name
                if age_range not in age_data:
                    age_data[age_range] = {
                        "age_range": age_range,
                        "cost": 0,
                        "clicks": 0,
                        "impressions": 0,
                        "conversions": 0,
                        "conversion_value": 0,
                    }
                age_data[age_range]["cost"] += row.metrics.cost_micros / 1_000_000
                age_data[age_range]["clicks"] += row.metrics.clicks
                age_data[age_range]["impressions"] += row.metrics.impressions
                age_data[age_range]["conversions"] += row.metrics.conversions
                age_data[age_range]["conversion_value"] += row.metrics.conversions_value

        except GoogleAdsException as e:
            print(f"Google Ads API error: {e}")
            raise

        results = []
        for age_range, data in age_data.items():
            data["ctr"] = (data["clicks"] / data["impressions"] * 100) if data["impressions"] > 0 else 0
            data["conv_rate"] = (data["conversions"] / data["clicks"] * 100) if data["clicks"] > 0 else 0
            results.append(data)

        return sorted(results, key=lambda x: x["cost"], reverse=True)

    def get_gender_performance(self, days: int = 30) -> list[dict[str, Any]]:
        """Get performance breakdown by gender.

        Returns:
            List of gender performance records.
        """
        ga_service = self._get_service("GoogleAdsService")

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        query = f"""
            SELECT
                ad_group_criterion.gender.type,
                metrics.cost_micros,
                metrics.clicks,
                metrics.impressions,
                metrics.conversions,
                metrics.conversions_value
            FROM gender_view
            WHERE segments.date BETWEEN '{start_date.strftime('%Y-%m-%d')}' AND '{end_date.strftime('%Y-%m-%d')}'
        """

        gender_data = {}
        try:
            response = ga_service.search(customer_id=self.customer_id, query=query)
            for row in response:
                gender = row.ad_group_criterion.gender.type.name
                if gender not in gender_data:
                    gender_data[gender] = {
                        "gender": gender,
                        "cost": 0,
                        "clicks": 0,
                        "impressions": 0,
                        "conversions": 0,
                        "conversion_value": 0,
                    }
                gender_data[gender]["cost"] += row.metrics.cost_micros / 1_000_000
                gender_data[gender]["clicks"] += row.metrics.clicks
                gender_data[gender]["impressions"] += row.metrics.impressions
                gender_data[gender]["conversions"] += row.metrics.conversions
                gender_data[gender]["conversion_value"] += row.metrics.conversions_value

        except GoogleAdsException as e:
            print(f"Google Ads API error: {e}")
            raise

        results = []
        for gender, data in gender_data.items():
            data["ctr"] = (data["clicks"] / data["impressions"] * 100) if data["impressions"] > 0 else 0
            data["conv_rate"] = (data["conversions"] / data["clicks"] * 100) if data["clicks"] > 0 else 0
            results.append(data)

        return sorted(results, key=lambda x: x["cost"], reverse=True)

    def get_location_performance(self, days: int = 30, limit: int = 10) -> list[dict[str, Any]]:
        """Get performance breakdown by location (country/region).

        Returns:
            List of location performance records.
        """
        ga_service = self._get_service("GoogleAdsService")

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        query = f"""
            SELECT
                geographic_view.country_criterion_id,
                geographic_view.location_type,
                metrics.cost_micros,
                metrics.clicks,
                metrics.impressions,
                metrics.conversions,
                metrics.conversions_value
            FROM geographic_view
            WHERE segments.date BETWEEN '{start_date.strftime('%Y-%m-%d')}' AND '{end_date.strftime('%Y-%m-%d')}'
        """

        location_data = {}
        try:
            response = ga_service.search(customer_id=self.customer_id, query=query)
            for row in response:
                location_id = str(row.geographic_view.country_criterion_id)
                if location_id not in location_data:
                    location_data[location_id] = {
                        "location_id": location_id,
                        "location_type": row.geographic_view.location_type.name,
                        "cost": 0,
                        "clicks": 0,
                        "impressions": 0,
                        "conversions": 0,
                        "conversion_value": 0,
                    }
                location_data[location_id]["cost"] += row.metrics.cost_micros / 1_000_000
                location_data[location_id]["clicks"] += row.metrics.clicks
                location_data[location_id]["impressions"] += row.metrics.impressions
                location_data[location_id]["conversions"] += row.metrics.conversions
                location_data[location_id]["conversion_value"] += row.metrics.conversions_value

        except GoogleAdsException as e:
            print(f"Google Ads API error: {e}")
            raise

        results = []
        for location_id, data in location_data.items():
            data["ctr"] = (data["clicks"] / data["impressions"] * 100) if data["impressions"] > 0 else 0
            data["conv_rate"] = (data["conversions"] / data["clicks"] * 100) if data["clicks"] > 0 else 0
            results.append(data)

        return sorted(results, key=lambda x: x["cost"], reverse=True)[:limit]

    def update_responsive_search_ad(
        self,
        ad_group_id: str,
        ad_id: str,
        current_headlines: list[str],
        new_headlines: list[str],
        current_descriptions: list[str],
        new_descriptions: list[str],
    ) -> bool:
        """Update a responsive search ad by adding new headlines and descriptions.

        Args:
            ad_group_id: The ad group ID.
            ad_id: The ad ID.
            current_headlines: Existing headlines in the ad.
            new_headlines: New headlines to add.
            current_descriptions: Existing descriptions in the ad.
            new_descriptions: New descriptions to add.

        Returns:
            True if successful.
        """
        ad_group_ad_service = self._get_service("AdGroupAdService")

        # Merge headlines (avoid duplicates, max 15)
        all_headlines = list(current_headlines)
        for headline in new_headlines:
            if headline not in all_headlines and len(all_headlines) < 15:
                all_headlines.append(headline)

        # Merge descriptions (avoid duplicates, max 4)
        all_descriptions = list(current_descriptions)
        for desc in new_descriptions:
            if desc not in all_descriptions and len(all_descriptions) < 4:
                all_descriptions.append(desc)

        # Build the resource name
        resource_name = ad_group_ad_service.ad_group_ad_path(
            self.customer_id, ad_group_id, ad_id
        )

        # Create the operation
        operation = self.client.get_type("AdGroupAdOperation")
        ad_group_ad = operation.update
        ad_group_ad.resource_name = resource_name

        # Build headline assets - use proto-plus style
        for headline_text in all_headlines:
            headline_asset = self.client.get_type("AdTextAsset")
            headline_asset.text = headline_text
            ad_group_ad.ad.responsive_search_ad.headlines.append(headline_asset)

        # Build description assets
        for desc_text in all_descriptions:
            desc_asset = self.client.get_type("AdTextAsset")
            desc_asset.text = desc_text
            ad_group_ad.ad.responsive_search_ad.descriptions.append(desc_asset)

        # Set the field mask for what we're updating
        from google.protobuf import field_mask_pb2
        field_mask = field_mask_pb2.FieldMask(
            paths=["ad.responsive_search_ad.headlines", "ad.responsive_search_ad.descriptions"]
        )
        operation.update_mask.CopyFrom(field_mask)

        try:
            response = ad_group_ad_service.mutate_ad_group_ads(
                customer_id=self.customer_id,
                operations=[operation],
            )
            print(f"Updated RSA: {response.results[0].resource_name}")
            return True
        except GoogleAdsException as e:
            print(f"Failed to update RSA: {e}")
            for error in e.failure.errors:
                print(f"  Error: {error.message}")
            return False
