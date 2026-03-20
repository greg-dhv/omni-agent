"""SEO Content Executor - sends content to client via email."""

import logging
from datetime import datetime
from typing import Any

from core.models import Action, AgentType, Content
from core.supabase import SupabaseRepository
from core.email import send_email, create_content_email_html
from .writer import SEOContentWriter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SEOContentExecutor:
    """Executes SEO content recommendations."""

    def __init__(self):
        self.repo = SupabaseRepository()
        self.writer = SEOContentWriter()

    async def execute_keyword_approval(self, recommendation: dict) -> dict:
        """Execute keyword approval - generates content.

        Args:
            recommendation: Approved keyword recommendation.

        Returns:
            Action dict recording what was done.
        """
        logger.info(f"Generating content for recommendation: {recommendation.get('id')}")

        action = Action(
            recommendation_id=recommendation.get("id"),
            agent=AgentType.SEO_CONTENT,
            action_type="generate_content",
            title=f"Generated article for '{recommendation.get('details', {}).get('keyword')}'",
        )

        try:
            # Generate multilingual content
            content = await self.writer.generate_content_for_recommendation(recommendation)

            # Save to database
            self.repo.create_content(content.to_db_dict())

            action.description = f"Created draft article in EN/FR/NL"
            action.impact = "Content ready for review and approval"
            action.result = "success"
            action.metadata = {"content_id": content.id}

        except Exception as e:
            logger.error(f"Content generation failed: {e}")
            action.result = "failed"
            action.error_message = str(e)

        action.executed_at = datetime.utcnow()
        return action.to_db_dict()

    async def send_content_to_client(self, content: dict) -> dict:
        """Send approved content to client via email.

        Args:
            content: The content record to send.

        Returns:
            Action dict recording what was done.
        """
        logger.info(f"Sending content to client: {content.get('id')}")

        action = Action(
            recommendation_id=content.get("recommendation_id"),
            agent=AgentType.SEO_CONTENT,
            action_type="send_content",
            title=f"Sent article '{content.get('title_en')}'",
        )

        try:
            # Get client settings
            client_settings = self.repo.get_setting("client_email") or {}
            email_settings = self.repo.get_setting("email_settings") or {}

            client_email = client_settings.get("email")
            client_name = client_settings.get("name", "Client")

            if not client_email:
                raise ValueError("Client email not configured")

            # Create and send email
            html_content = create_content_email_html(content, client_name)

            success = await send_email(
                to_email=client_email,
                to_name=client_name,
                subject=f"New Blog Article Ready: {content.get('title_en', content.get('keyword'))}",
                html_content=html_content,
                from_email=email_settings.get("from_email"),
                from_name=email_settings.get("from_name", "AI Ops"),
                provider=email_settings.get("provider", "sendgrid"),
            )

            if success:
                # Update content status
                self.repo.update_content_status(
                    content.get("id"),
                    "sent",
                    sent_to=client_email,
                    sent_at=datetime.utcnow().isoformat(),
                )

                action.description = f"Sent article to {client_email}"
                action.impact = "Content delivered to client"
                action.result = "success"
            else:
                raise Exception("Email sending failed")

        except Exception as e:
            logger.error(f"Content delivery failed: {e}")
            action.result = "failed"
            action.error_message = str(e)

        action.executed_at = datetime.utcnow()
        return action.to_db_dict()

    async def execute(self, recommendation: dict) -> dict:
        """Execute a recommendation based on its type.

        Args:
            recommendation: The approved recommendation.

        Returns:
            Action dict recording what was done.
        """
        rec_type = recommendation.get("type")

        if rec_type == "keyword_opportunity":
            return await self.execute_keyword_approval(recommendation)
        else:
            logger.warning(f"Unknown recommendation type: {rec_type}")
            return Action(
                recommendation_id=recommendation.get("id"),
                agent=AgentType.SEO_CONTENT,
                action_type=rec_type,
                result="failed",
                error_message=f"Unknown type: {rec_type}",
            ).to_db_dict()

    async def process_approved_content(self):
        """Process all approved content (send to client)."""
        approved_content = self.repo.get_approved_content()

        if not approved_content:
            logger.info("No approved content to send")
            return {"sent": 0, "failed": 0}

        sent = 0
        failed = 0

        for content in approved_content:
            try:
                action = await self.send_content_to_client(content)
                self.repo.create_action(action)

                if action.get("result") == "success":
                    sent += 1
                else:
                    failed += 1
            except Exception as e:
                logger.error(f"Failed to process content {content.get('id')}: {e}")
                failed += 1

        return {"sent": sent, "failed": failed}
