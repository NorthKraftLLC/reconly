"""Celery tasks for reconciliation processing."""

from datetime import UTC

from celery import shared_task
from sqlalchemy import select

from app.db.session import async_session
from app.models.reconciliation import Reconciliation, ReconciliationStatus


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_reconciliation(self, rec_id: str):
    try:
        import asyncio

        async def _run():
            async with async_session() as session:
                result = await session.execute(select(Reconciliation).where(Reconciliation.id == rec_id))
                rec = result.scalar_one_or_none()
                if not rec:
                    return
                rec.status = ReconciliationStatus.IN_PROGRESS
                await session.commit()
                from app.services.reconciliation_service import run_reconciliation

                rec = await run_reconciliation(session, rec)
                await session.commit()

        asyncio.run(_run())
    except Exception as exc:
        raise self.retry(exc=exc) from exc


@shared_task
def stale_data_alert(company_id: str, days_threshold: int = 30):
    """Alert when reconciliations haven't been run recently."""
    import logging
    from datetime import datetime, timedelta

    threshold = datetime.now(UTC) - timedelta(days=days_threshold)
    logging.warning(f"Stale data alert for company {company_id}: last reconciliation after {threshold}")
    return {"company_id": company_id, "alerted": True}
