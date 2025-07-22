"""Stripe checkout router - Open Source Stub."""

from typing import Any

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel


class CheckoutSessionRequest(BaseModel):
    priceId: str
    plan: str
    userEmail: str


class PortalSessionRequest(BaseModel):
    userEmail: str


class StripeCheckoutRouter:
    """Router for handling Stripe checkout sessions - Open Source Stub."""

    def __init__(self):
        self.router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        """Set up API routes."""
        self.router.post("/create-checkout-session")(
            self.create_checkout_session)
        self.router.post("/create-portal-session")(self.create_portal_session)

    async def create_checkout_session(
            self, request: Request,
            checkout_data: CheckoutSessionRequest) -> dict[str, Any]:
        """Create a Stripe checkout session - stub implementation."""
        raise HTTPException(
            status_code=501,
            detail=("Stripe checkout is not available in the open source "
                    "version. Please upgrade to the enterprise edition."))

    async def create_portal_session(
            self, request: Request,
            portal_data: PortalSessionRequest) -> dict[str, Any]:
        """Create a Stripe billing portal session - stub implementation."""
        raise HTTPException(
            status_code=501,
            detail=(
                "Stripe billing portal is not available in the open source "
                "version. Please upgrade to the enterprise edition."))
