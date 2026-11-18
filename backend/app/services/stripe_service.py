"""Stripe service for payments."""

import stripe

from app.config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY or "sk_test_placeholder"


def create_checkout_session(plan_id: str, success_url: str, cancel_url: str):
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{"price": plan_id, "quantity": 1}],
        mode="subscription",
        success_url=success_url,
        cancel_url=cancel_url,
    )
    return session


def verify_webhook_signature(payload: bytes, sig_header: str):
    event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET or "whsec_placeholder")
    return event


def handle_customer_subscription(event):
    subscription = event.data.object
    customer_id = subscription.customer
    status = subscription.status
    return {"customer_id": customer_id, "status": status, "subscription_id": subscription.id}


def check_entitlements(user_id: str, resource: str) -> bool:
    """Check if user has access to a resource based on their plan tier."""
    return True  # Allow for now (free tier during dev)
