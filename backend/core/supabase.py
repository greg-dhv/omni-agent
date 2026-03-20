"""Supabase client for AI Ops Platform."""

import os
from functools import lru_cache
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()


@lru_cache()
def get_supabase_client() -> Client:
    """Get a singleton Supabase client using service role key."""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

    if not url or not key:
        raise ValueError(
            "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in environment"
        )

    return create_client(url, key)


class SupabaseRepository:
    """Repository for Supabase database operations."""

    def __init__(self):
        self.client = get_supabase_client()

    # ==================== Recommendations ====================

    def create_recommendation(self, recommendation: dict) -> dict:
        """Insert a new recommendation."""
        result = self.client.table("recommendations").insert(recommendation).execute()
        return result.data[0] if result.data else None

    def create_recommendations(self, recommendations: list[dict]) -> list[dict]:
        """Insert multiple recommendations."""
        if not recommendations:
            return []
        result = self.client.table("recommendations").insert(recommendations).execute()
        return result.data

    def get_pending_recommendations(self, agent: str = None) -> list[dict]:
        """Get all pending recommendations, optionally filtered by agent."""
        query = self.client.table("recommendations").select("*").eq("status", "pending")
        if agent:
            query = query.eq("agent", agent)
        result = query.order("created_at", desc=True).execute()
        return result.data

    def get_approved_recommendations(self, agent: str = None) -> list[dict]:
        """Get all approved recommendations waiting for execution."""
        query = self.client.table("recommendations").select("*").eq("status", "approved")
        if agent:
            query = query.eq("agent", agent)
        result = query.order("reviewed_at", desc=False).execute()
        return result.data

    def update_recommendation_status(
        self, recommendation_id: str, status: str, executed_at: str = None
    ) -> dict:
        """Update recommendation status."""
        update_data = {"status": status}
        if executed_at:
            update_data["executed_at"] = executed_at
        result = (
            self.client.table("recommendations")
            .update(update_data)
            .eq("id", recommendation_id)
            .execute()
        )
        return result.data[0] if result.data else None

    # ==================== Actions ====================

    def create_action(self, action: dict) -> dict:
        """Log an executed action."""
        result = self.client.table("actions").insert(action).execute()
        return result.data[0] if result.data else None

    def get_recent_actions(self, limit: int = 10, agent: str = None) -> list[dict]:
        """Get recent actions."""
        query = self.client.table("actions").select("*")
        if agent:
            query = query.eq("agent", agent)
        result = query.order("executed_at", desc=True).limit(limit).execute()
        return result.data

    # ==================== Performance Snapshots ====================

    def upsert_performance_snapshot(self, snapshot: dict) -> dict:
        """Upsert a performance snapshot (update if date+source+client_id exists)."""
        try:
            # Try upsert with multi-client constraint
            result = (
                self.client.table("performance_snapshots")
                .upsert(snapshot, on_conflict="date,source,client_id")
                .execute()
            )
            return result.data[0] if result.data else None
        except Exception:
            # Fallback to simple insert if constraint doesn't match
            result = (
                self.client.table("performance_snapshots")
                .insert(snapshot)
                .execute()
            )
            return result.data[0] if result.data else None

    def get_performance_snapshots(
        self, source: str, start_date: str, end_date: str = None
    ) -> list[dict]:
        """Get performance snapshots for a date range."""
        query = (
            self.client.table("performance_snapshots")
            .select("*")
            .eq("source", source)
            .gte("date", start_date)
        )
        if end_date:
            query = query.lte("date", end_date)
        result = query.order("date", desc=False).execute()
        return result.data

    # ==================== Content ====================

    def create_content(self, content: dict) -> dict:
        """Create a new content entry."""
        result = self.client.table("content").insert(content).execute()
        return result.data[0] if result.data else None

    def get_content_by_status(self, status: str) -> list[dict]:
        """Get content by status."""
        result = (
            self.client.table("content")
            .select("*")
            .eq("status", status)
            .order("created_at", desc=True)
            .execute()
        )
        return result.data

    def get_approved_content(self) -> list[dict]:
        """Get content that's been approved and needs to be sent."""
        result = (
            self.client.table("content")
            .select("*")
            .eq("status", "approved")
            .order("updated_at", desc=False)
            .execute()
        )
        return result.data

    def update_content_status(
        self, content_id: str, status: str, sent_to: str = None, sent_at: str = None
    ) -> dict:
        """Update content status."""
        update_data = {"status": status, "updated_at": sent_at or "now()"}
        if sent_to:
            update_data["sent_to"] = sent_to
        if sent_at:
            update_data["sent_at"] = sent_at
        result = (
            self.client.table("content")
            .update(update_data)
            .eq("id", content_id)
            .execute()
        )
        return result.data[0] if result.data else None

    # ==================== Job Runs ====================

    def create_job_run(self, job_run: dict) -> dict:
        """Start tracking a job run."""
        result = self.client.table("job_runs").insert(job_run).execute()
        return result.data[0] if result.data else None

    def complete_job_run(
        self, job_id: str, status: str, summary: dict = None, error_message: str = None
    ) -> dict:
        """Complete a job run."""
        from datetime import datetime

        update_data = {
            "status": status,
            "completed_at": datetime.utcnow().isoformat(),
        }
        if summary:
            update_data["summary"] = summary
        if error_message:
            update_data["error_message"] = error_message

        result = (
            self.client.table("job_runs")
            .update(update_data)
            .eq("id", job_id)
            .execute()
        )
        return result.data[0] if result.data else None

    # ==================== Settings ====================

    def get_setting(self, key: str) -> dict:
        """Get a setting by key."""
        try:
            result = (
                self.client.table("settings")
                .select("value")
                .eq("key", key)
                .execute()
            )
            if result.data and len(result.data) > 0:
                return result.data[0].get("value")
            return None
        except Exception:
            return None

    def get_all_settings(self) -> dict[str, dict]:
        """Get all settings as a dictionary."""
        result = self.client.table("settings").select("*").execute()
        return {row["key"]: row["value"] for row in result.data}

    # ==================== Clients ====================

    def get_client(self, client_id: str) -> dict:
        """Get a client by ID."""
        result = (
            self.client.table("clients")
            .select("*")
            .eq("id", client_id)
            .single()
            .execute()
        )
        return result.data

    def get_client_by_slug(self, slug: str) -> dict:
        """Get a client by slug."""
        result = (
            self.client.table("clients")
            .select("*")
            .eq("slug", slug)
            .eq("active", True)
            .single()
            .execute()
        )
        return result.data

    def get_all_active_clients(self) -> list[dict]:
        """Get all active clients."""
        result = (
            self.client.table("clients")
            .select("*")
            .eq("active", True)
            .order("name")
            .execute()
        )
        return result.data

    def create_client(self, client_data: dict) -> dict:
        """Create a new client."""
        result = self.client.table("clients").insert(client_data).execute()
        return result.data[0] if result.data else None

    def update_client(self, client_id: str, client_data: dict) -> dict:
        """Update a client."""
        client_data["updated_at"] = "now()"
        result = (
            self.client.table("clients")
            .update(client_data)
            .eq("id", client_id)
            .execute()
        )
        return result.data[0] if result.data else None

    def get_client_google_ads_credentials(self, client_id: str) -> dict:
        """Get Google Ads credentials for a client."""
        result = (
            self.client.table("clients")
            .select("google_ads_customer_id, google_ads_login_customer_id, google_ads_refresh_token")
            .eq("id", client_id)
            .single()
            .execute()
        )
        return result.data

    # ==================== Client-scoped queries ====================

    def get_pending_recommendations_for_client(
        self, client_id: str, agent: str = None
    ) -> list[dict]:
        """Get pending recommendations for a specific client."""
        query = (
            self.client.table("recommendations")
            .select("*")
            .eq("status", "pending")
            .eq("client_id", client_id)
        )
        if agent:
            query = query.eq("agent", agent)
        result = query.order("created_at", desc=True).execute()
        return result.data

    def get_recent_actions_for_client(
        self, client_id: str, limit: int = 10, agent: str = None
    ) -> list[dict]:
        """Get recent actions for a specific client."""
        query = self.client.table("actions").select("*").eq("client_id", client_id)
        if agent:
            query = query.eq("agent", agent)
        result = query.order("executed_at", desc=True).limit(limit).execute()
        return result.data

    def get_performance_snapshots_for_client(
        self, client_id: str, source: str, start_date: str, end_date: str = None
    ) -> list[dict]:
        """Get performance snapshots for a specific client."""
        query = (
            self.client.table("performance_snapshots")
            .select("*")
            .eq("client_id", client_id)
            .eq("source", source)
            .gte("date", start_date)
        )
        if end_date:
            query = query.lte("date", end_date)
        result = query.order("date", desc=False).execute()
        return result.data

    def get_content_for_client(self, client_id: str, status: str = None) -> list[dict]:
        """Get content for a specific client."""
        query = self.client.table("content").select("*").eq("client_id", client_id)
        if status:
            query = query.eq("status", status)
        result = query.order("created_at", desc=True).execute()
        return result.data

    # ==================== Consultant-Client relationships ====================

    def add_consultant_to_client(
        self, consultant_id: str, client_id: str, role: str = "manager"
    ) -> dict:
        """Link a consultant to a client."""
        result = (
            self.client.table("consultant_clients")
            .insert({
                "consultant_id": consultant_id,
                "client_id": client_id,
                "role": role
            })
            .execute()
        )
        return result.data[0] if result.data else None

    def get_consultant_clients(self, consultant_id: str) -> list[dict]:
        """Get all clients for a consultant."""
        result = (
            self.client.table("consultant_clients")
            .select("*, clients(*)")
            .eq("consultant_id", consultant_id)
            .execute()
        )
        return result.data
