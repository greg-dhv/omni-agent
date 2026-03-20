"""Base agent class for AI Ops Platform."""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from core.models import JobRun, JobStatus, AgentType
from core.supabase import SupabaseRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all AI agents."""

    def __init__(self, agent_type: AgentType):
        self.agent_type = agent_type
        self.repo = SupabaseRepository()
        self.job_run: JobRun | None = None

    @abstractmethod
    async def analyze(self) -> list[dict]:
        """Run analysis and generate recommendations.

        Returns:
            List of recommendation dicts ready for database insertion.
        """
        pass

    @abstractmethod
    async def execute(self, recommendation: dict) -> dict:
        """Execute an approved recommendation.

        Args:
            recommendation: The approved recommendation to execute.

        Returns:
            Action dict recording what was done.
        """
        pass

    async def run_analysis(self) -> dict:
        """Run the full analysis pipeline."""
        # Start job run tracking
        self.job_run = JobRun(agent=self.agent_type, status=JobStatus.RUNNING)
        self.repo.create_job_run(self.job_run.to_db_dict())

        try:
            logger.info(f"Starting analysis for {self.agent_type.value}")

            # Run analysis
            recommendations = await self.analyze()

            # Save recommendations to database
            if recommendations:
                self.repo.create_recommendations(recommendations)
                logger.info(f"Created {len(recommendations)} recommendations")

            # Complete job run
            summary = {
                "recommendations_created": len(recommendations),
                "timestamp": datetime.utcnow().isoformat(),
            }
            self.repo.complete_job_run(
                self.job_run.id,
                JobStatus.COMPLETED.value,
                summary=summary,
            )

            logger.info(f"Analysis completed for {self.agent_type.value}")
            return summary

        except Exception as e:
            logger.error(f"Analysis failed for {self.agent_type.value}: {e}")
            self.repo.complete_job_run(
                self.job_run.id,
                JobStatus.FAILED.value,
                error_message=str(e),
            )
            raise

    async def run_executor(self) -> dict:
        """Execute all approved recommendations for this agent."""
        approved = self.repo.get_approved_recommendations(self.agent_type.value)

        if not approved:
            logger.info(f"No approved recommendations for {self.agent_type.value}")
            return {"executed": 0, "failed": 0}

        executed = 0
        failed = 0

        for rec in approved:
            try:
                logger.info(f"Executing recommendation: {rec['id']}")
                action = await self.execute(rec)

                # Save action
                self.repo.create_action(action)

                # Update recommendation status
                self.repo.update_recommendation_status(
                    rec["id"],
                    "executed",
                    executed_at=datetime.utcnow().isoformat(),
                )

                executed += 1
                logger.info(f"Successfully executed: {rec['id']}")

            except Exception as e:
                logger.error(f"Failed to execute {rec['id']}: {e}")

                # Update recommendation as failed
                self.repo.update_recommendation_status(rec["id"], "failed")

                failed += 1

        return {"executed": executed, "failed": failed}
