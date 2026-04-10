"""
RTK-1 Billing Webhook Handler — Objective 85
Stripe webhook → activate customer_id → set subscription tier.
ITIL 4: Service Financial Management practice.
"""

import hashlib
import hmac
import os
from typing import Any, Dict

from app.core.logging import get_logger
from app.core.subscription import SubscriptionTier, subscription_manager

logger = get_logger("billing")

STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")

# Stripe price ID → RTK-1 tier mapping
PRICE_TO_TIER = {
    "price_starter_monthly": SubscriptionTier.STARTER,
    "price_professional_monthly": SubscriptionTier.PROFESSIONAL,
    "price_enterprise_monthly": SubscriptionTier.ENTERPRISE,
    "price_federal_monthly": SubscriptionTier.FEDERAL,
}


class BillingManager:
    """
    Handles Stripe webhook events to automate subscription lifecycle.
    Activation: Set STRIPE_WEBHOOK_SECRET in .env
    """

    def verify_stripe_signature(self, payload: bytes, sig_header: str) -> bool:
        """Verify Stripe webhook signature to prevent spoofing."""
        if not STRIPE_WEBHOOK_SECRET:
            logger.warning("stripe_webhook_secret_not_set")
            return True  # Allow in dev — require in production

        try:
            parts = {
                k: v for part in sig_header.split(",") for k, v in [part.split("=", 1)]
            }
            timestamp = parts.get("t", "")
            signatures = [v for k, v in parts.items() if k == "v1"]

            signed_payload = f"{timestamp}.{payload.decode('utf-8')}"
            expected = hmac.new(
                STRIPE_WEBHOOK_SECRET.encode("utf-8"),
                signed_payload.encode("utf-8"),
                hashlib.sha256,
            ).hexdigest()

            return any(hmac.compare_digest(expected, sig) for sig in signatures)
        except Exception as e:
            logger.error("stripe_signature_verification_failed", error=str(e))
            return False

    def handle_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Route Stripe events to appropriate handlers."""
        event_type = event.get("type", "")
        data = event.get("data", {}).get("object", {})

        handlers = {
            "checkout.session.completed": self._handle_checkout_completed,
            "customer.subscription.created": self._handle_subscription_created,
            "customer.subscription.updated": self._handle_subscription_updated,
            "customer.subscription.deleted": self._handle_subscription_cancelled,
            "invoice.payment_failed": self._handle_payment_failed,
        }

        handler = handlers.get(event_type)
        if handler:
            return handler(data)

        logger.info("stripe_event_unhandled", event_type=event_type)
        return {"status": "ignored", "event_type": event_type}

    def _handle_checkout_completed(self, data: Dict[str, Any]) -> Dict[str, Any]:
        customer_id = data.get("client_reference_id") or data.get("customer")
        price_id = self._extract_price_id(data)
        tier = PRICE_TO_TIER.get(price_id, SubscriptionTier.STARTER)
        email = data.get("customer_details", {}).get("email")

        sub = subscription_manager.create_subscription(
            customer_id=customer_id,
            tier=tier,
            billing_email=email,
        )

        logger.info(
            "subscription_activated",
            customer_id=customer_id,
            tier=tier.value,
            email=email,
        )

        return {
            "status": "activated",
            "customer_id": customer_id,
            "tier": tier.value,
            "api_key": sub.api_key,
        }

    def _handle_subscription_created(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self._handle_checkout_completed(data)

    def _handle_subscription_updated(self, data: Dict[str, Any]) -> Dict[str, Any]:
        customer_id = data.get("customer")
        price_id = self._extract_price_id(data)
        tier = PRICE_TO_TIER.get(price_id, SubscriptionTier.STARTER)
        logger.info(
            "subscription_updated", customer_id=customer_id, new_tier=tier.value
        )
        return {"status": "updated", "customer_id": customer_id, "tier": tier.value}

    def _handle_subscription_cancelled(self, data: Dict[str, Any]) -> Dict[str, Any]:
        customer_id = data.get("customer")
        logger.warning("subscription_cancelled", customer_id=customer_id)
        return {"status": "cancelled", "customer_id": customer_id}

    def _handle_payment_failed(self, data: Dict[str, Any]) -> Dict[str, Any]:
        customer_id = data.get("customer")
        logger.error("payment_failed", customer_id=customer_id)
        return {"status": "payment_failed", "customer_id": customer_id}

    def _extract_price_id(self, data: Dict[str, Any]) -> str:
        try:
            items = data.get("line_items", {}).get("data", [])
            if items:
                return items[0].get("price", {}).get("id", "")
            # From subscription object
            items = data.get("items", {}).get("data", [])
            if items:
                return items[0].get("price", {}).get("id", "")
        except Exception:
            pass
        return ""


billing_manager = BillingManager()
