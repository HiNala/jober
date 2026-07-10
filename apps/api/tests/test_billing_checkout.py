"""Unit tests for Stripe Checkout / portal session helpers (no live Stripe)."""

from __future__ import annotations

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from jober_api.auth.constants import DEFAULT_DEV_TENANT_ID, DEFAULT_DEV_USER_ID
from jober_api.config import settings
from jober_api.models.enums import PlanTier
from jober_api.services.billing import checkout as checkout_mod


@pytest.mark.asyncio
async def test_create_checkout_session_requires_stripe_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "stripe_secret_key", "")
    monkeypatch.setattr(settings, "stripe_price_pro_monthly", "price_test")
    session = AsyncMock()
    with pytest.raises(HTTPException) as exc:
        await checkout_mod.create_checkout_session(
            session,
            tenant_id=DEFAULT_DEV_TENANT_ID,
            user_id=DEFAULT_DEV_USER_ID,
            success_url="http://localhost:3000/pricing?checkout=success",
            cancel_url="http://localhost:3000/pricing?checkout=cancel",
        )
    assert exc.value.status_code == 503
    assert "not configured" in str(exc.value.detail).lower()


@pytest.mark.asyncio
async def test_create_checkout_session_requires_price(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "stripe_secret_key", "sk_test_fake")
    monkeypatch.setattr(settings, "stripe_price_pro_monthly", "")
    session = AsyncMock()
    with pytest.raises(HTTPException) as exc:
        await checkout_mod.create_checkout_session(
            session,
            tenant_id=DEFAULT_DEV_TENANT_ID,
            user_id=DEFAULT_DEV_USER_ID,
            success_url="http://localhost:3000/ok",
            cancel_url="http://localhost:3000/cancel",
        )
    assert exc.value.status_code == 503


@pytest.mark.asyncio
async def test_create_checkout_session_sets_tenant_metadata(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "stripe_secret_key", "sk_test_fake")
    monkeypatch.setattr(settings, "stripe_price_pro_monthly", "price_pro_monthly")

    tenant = SimpleNamespace(
        id=DEFAULT_DEV_TENANT_ID,
        name="Dev Tenant",
        stripe_customer_id="cus_existing",
        plan=PlanTier.FREE,
    )
    user = SimpleNamespace(id=DEFAULT_DEV_USER_ID, email="dev@jober.local")

    session = AsyncMock()

    async def _get(model, pk):  # noqa: ANN001
        if model.__name__ == "Tenant":
            return tenant
        if model.__name__ == "User":
            return user
        return None

    session.get = AsyncMock(side_effect=_get)

    created: dict = {}

    class FakeCheckoutSession:
        @staticmethod
        def create(**kwargs):  # noqa: ANN003
            created.update(kwargs)
            return {"url": "https://checkout.stripe.com/c/pay/cs_test_123"}

    class FakeStripe:
        api_key = ""
        checkout = SimpleNamespace(Session=FakeCheckoutSession)

    monkeypatch.setattr(checkout_mod, "_stripe_client", lambda: FakeStripe)

    result = await checkout_mod.create_checkout_session(
        session,
        tenant_id=DEFAULT_DEV_TENANT_ID,
        user_id=DEFAULT_DEV_USER_ID,
        success_url="http://localhost:3000/pricing?checkout=success",
        cancel_url="http://localhost:3000/pricing?checkout=cancel",
    )

    assert result["url"].startswith("https://checkout.stripe.com/")
    assert created["metadata"]["tenant_id"] == str(DEFAULT_DEV_TENANT_ID)
    assert created["metadata"]["user_id"] == str(DEFAULT_DEV_USER_ID)
    assert created["client_reference_id"] == str(DEFAULT_DEV_TENANT_ID)
    assert created["line_items"][0]["price"] == "price_pro_monthly"
    assert created["customer"] == "cus_existing"
    assert created["mode"] == "subscription"


@pytest.mark.asyncio
async def test_create_checkout_creates_customer_when_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "stripe_secret_key", "sk_test_fake")
    monkeypatch.setattr(settings, "stripe_price_pro_monthly", "price_pro_monthly")

    tenant = SimpleNamespace(
        id=DEFAULT_DEV_TENANT_ID,
        name="Dev Tenant",
        stripe_customer_id=None,
        plan=PlanTier.FREE,
    )
    user = SimpleNamespace(id=DEFAULT_DEV_USER_ID, email="dev@jober.local")
    session = AsyncMock()
    session.flush = AsyncMock()

    async def _get(model, pk):  # noqa: ANN001
        if model.__name__ == "Tenant":
            return tenant
        if model.__name__ == "User":
            return user
        return None

    session.get = AsyncMock(side_effect=_get)

    customer_kwargs: dict = {}

    class FakeCustomer:
        @staticmethod
        def create(**kwargs):  # noqa: ANN003
            customer_kwargs.update(kwargs)
            return {"id": "cus_new_123"}

    class FakeCheckoutSession:
        @staticmethod
        def create(**kwargs):  # noqa: ANN003
            return {"url": "https://checkout.stripe.com/c/pay/cs_new"}

    class FakeStripe:
        api_key = ""
        Customer = FakeCustomer
        checkout = SimpleNamespace(Session=FakeCheckoutSession)

    monkeypatch.setattr(checkout_mod, "_stripe_client", lambda: FakeStripe)

    result = await checkout_mod.create_checkout_session(
        session,
        tenant_id=DEFAULT_DEV_TENANT_ID,
        user_id=DEFAULT_DEV_USER_ID,
        success_url="http://localhost:3000/ok",
        cancel_url="http://localhost:3000/cancel",
    )

    assert result["url"]
    assert tenant.stripe_customer_id == "cus_new_123"
    assert customer_kwargs["metadata"]["tenant_id"] == str(DEFAULT_DEV_TENANT_ID)
    session.flush.assert_awaited()


@pytest.mark.asyncio
async def test_create_portal_session_requires_customer(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "stripe_secret_key", "sk_test_fake")
    monkeypatch.setattr(settings, "stripe_price_pro_monthly", "price_pro_monthly")

    tenant = SimpleNamespace(id=DEFAULT_DEV_TENANT_ID, stripe_customer_id=None)
    session = AsyncMock()
    session.get = AsyncMock(return_value=tenant)

    with pytest.raises(HTTPException) as exc:
        await checkout_mod.create_portal_session(
            session,
            tenant_id=DEFAULT_DEV_TENANT_ID,
            return_url="http://localhost:3000/settings",
        )
    assert exc.value.status_code == 400


def test_stripe_enabled_flag(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "stripe_secret_key", "")
    monkeypatch.setattr(settings, "stripe_price_pro_monthly", "price_x")
    assert checkout_mod.stripe_enabled() is False

    monkeypatch.setattr(settings, "stripe_secret_key", "sk_test")
    monkeypatch.setattr(settings, "stripe_price_pro_monthly", "")
    assert checkout_mod.stripe_enabled() is False

    monkeypatch.setattr(settings, "stripe_secret_key", "sk_test")
    monkeypatch.setattr(settings, "stripe_price_pro_monthly", "price_x")
    assert checkout_mod.stripe_enabled() is True


def test_startup_requires_webhook_secret_when_stripe_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from jober_api.config import Settings
    from jober_api.privacy.secrets_check import validate_startup_secrets

    monkeypatch.setenv("CI", "")
    prod_settings = Settings(
        jober_env="production",
        auth_mode="native",
        cookie_secure=True,
        vault_encryption_key="real-key-value-here-32chars!!",
        secret_key="real-secret-key-value-here!!",
        minio_access_key="prod-minio-key",
        minio_secret_key="prod-minio-secret",
        stripe_secret_key="sk_live_fake",
        stripe_webhook_secret="",
    )
    monkeypatch.setattr("jober_api.privacy.secrets_check.settings", prod_settings)
    with pytest.raises(RuntimeError, match="STRIPE_WEBHOOK_SECRET"):
        validate_startup_secrets()


@pytest.mark.asyncio
async def test_checkout_completed_webhook_upgrades_via_metadata() -> None:
    """Pure unit path: metadata tenant_id is preferred (mocked session.get)."""
    from jober_api.services.billing.stripe_webhook import _checkout_completed

    tenant_id = uuid.uuid4()
    tenant = MagicMock()
    tenant.id = tenant_id
    tenant.stripe_customer_id = None
    tenant.plan = PlanTier.FREE

    session = AsyncMock()
    session.get = AsyncMock(return_value=tenant)
    session.flush = AsyncMock()

    # record_audit is async — patch it to no-op
    from jober_api.services.billing import stripe_webhook as wh

    async def _noop_audit(*_a, **_k):  # noqa: ANN001
        return None

    # Inline monkeypatch via attribute swap
    original = wh.record_audit
    wh.record_audit = _noop_audit  # type: ignore[assignment]
    try:
        result = await _checkout_completed(
            session,
            {
                "customer": "cus_meta",
                "metadata": {"tenant_id": str(tenant_id)},
            },
        )
    finally:
        wh.record_audit = original  # type: ignore[assignment]

    assert result["status"] == "upgraded"
    assert tenant.plan == PlanTier.PRO
    assert tenant.stripe_customer_id == "cus_meta"
