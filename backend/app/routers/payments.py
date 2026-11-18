"""Payments router."""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_session
from app.services.stripe_service import create_checkout_session, verify_webhook_signature, handle_customer_subscription
from app.config import settings
from app.core.audit import log_event

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/checkout")
async def checkout(plan_id: str, request: Request):
    success_url = f"{settings.FRONTEND_URL}/dashboard?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{settings.FRONTEND_URL}/billing"
    try:
        session = create_checkout_session(plan_id, success_url, cancel_url)
        return {"url": session.url, "session_id": session.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stripe error: {str(e)}")


@router.post("/webhook")
async def webhook(request: Request, db: AsyncSession = Depends(get_async_session)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")
    try:
        event = verify_webhook_signature(payload, sig_header)
    except (ValueError, Exception):
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event.type == "customer.subscription.created":
        result = handle_customer_subscription(event)
        log_event("stripe", "subscription_created", result["customer_id"], "success")
    elif event.type == "customer.subscription.updated":
        result = handle_customer_subscription(event)
        log_event("stripe", "subscription_updated", result["customer_id"], "success")
    elif event.type == "customer.subscription.deleted":
        log_event("stripe", "subscription_deleted", event.data.object.customer, "success")
    return {"status": "ok"}
