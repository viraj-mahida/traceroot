"""Stripe webhook router - Open Source Stub."""

from typing import Any

from fastapi import APIRouter, HTTPException, Request
from slowapi import Limiter

from rest.config.rate_limit import get_rate_limit_config


class StripeWebhookRouter:
    """Router for handling Stripe webhook events - Open Source Stub."""

    def __init__(self, limiter: Limiter):
        self.router = APIRouter()
        self.limiter = limiter
        self.rate_limit_config = get_rate_limit_config()
        self._setup_routes()

    def _setup_routes(self):
        """Set up API routes."""
        # Stripe webhook endpoint - stub implementation
        self.router.post("/stripe")(self.limiter.limit("100/minute")(
            self.stripe_webhook))

    async def stripe_webhook(self, request: Request) -> dict[str, Any]:
        """Handle Stripe webhook events - stub implementation."""
        raise HTTPException(
            status_code=501,
            detail=("Stripe webhooks are not available in the open source "
                    "version. Please upgrade to the enterprise edition."))
