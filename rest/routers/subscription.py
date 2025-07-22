"""Subscription management router - Open Source Stub."""

from typing import Any

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from slowapi import Limiter

from rest.config.rate_limit import get_rate_limit_config


class SubscriptionRequest(BaseModel):
    user_email: str
    payment_email: str
    hasAccess: bool
    subscription_plan: str
    start_date: str


class UpdateSubscriptionRequest(BaseModel):
    user_email: str
    hasAccess: bool
    subscription_plan: str
    start_date: str


class PaymentRecordRequest(BaseModel):
    user_email: str
    amount: int
    date: str
    stripe_payment_id: str


class SubscriptionRouter:
    """Router for managing user subscriptions - Open Source Stub."""

    def __init__(self, limiter: Limiter):
        self.router = APIRouter()
        self.limiter = limiter
        self.rate_limit_config = get_rate_limit_config()
        self._setup_routes()

    def _setup_routes(self):
        """Set up API routes."""
        # Apply rate limiting to routes
        self.router.post("/create")(self.limiter.limit("20/minute")(
            self.create_subscription))
        self.router.post("/update")(self.limiter.limit("30/minute")(
            self.update_subscription))
        self.router.post("/payment")(self.limiter.limit("30/minute")(
            self.record_payment))
        self.router.get("/get")(self.limiter.limit("60/minute")(
            self.get_subscription))

    async def create_subscription(
        self,
        request: Request,
        req_data: SubscriptionRequest,
    ) -> dict[str, Any]:
        """Create a new subscription - stub implementation."""
        raise HTTPException(
            status_code=501,
            detail=(
                "Subscription management is not available in the open source "
                "version. Please upgrade to the enterprise edition."))

    async def update_subscription(
        self,
        request: Request,
        req_data: UpdateSubscriptionRequest,
    ) -> dict[str, Any]:
        """Update an existing subscription - stub implementation."""
        raise HTTPException(
            status_code=501,
            detail=(
                "Subscription management is not available in the open "
                "source version. Please upgrade to the enterprise edition."))

    async def record_payment(
        self,
        request: Request,
        req_data: PaymentRecordRequest,
    ) -> dict[str, Any]:
        """Record a payment for a subscription - stub implementation."""
        raise HTTPException(
            status_code=501,
            detail=("Payment recording is not available in the open source "
                    "version. Please upgrade to the enterprise edition."))

    async def get_subscription(
        self,
        request: Request,
        user_email: str,
    ) -> dict[str, Any]:
        """Get subscription information for a user - stub implementation."""
        raise HTTPException(
            status_code=501,
            detail=(
                "Subscription information is not available in the open "
                "source version. Please upgrade to the enterprise edition."))
