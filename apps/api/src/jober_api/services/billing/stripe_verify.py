from __future__ import annotations

from typing import Any

from jober_api.config import settings


def construct_stripe_event(payload: bytes, signature: str) -> dict[str, Any]:
    """Parse and verify a Stripe webhook payload. Typed wrapper for mypy."""
    import stripe

    # stripe stubs omit Webhook.construct_event types; isolate the ignore here.
    event = stripe.Webhook.construct_event(  # type: ignore[no-untyped-call]
        payload, signature, settings.stripe_webhook_secret
    )
    return dict(event)
