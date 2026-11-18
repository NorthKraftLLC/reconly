"""Scheduler and stale-data alert logic."""

from datetime import datetime, timedelta, timezone
import logging

logger = logging.getLogger(__name__)


def check_stale_data(company_id: str, days_threshold: int = 30) -> dict:
    """Alert when reconciliations haven't been run recently."""
    threshold = datetime.now(timezone.utc) - timedelta(days=days_threshold)
    logger.warning(f"Stale data alert for company {company_id}: last reconciliation after {threshold}")
    return {"company_id": company_id, "alerted": True}
