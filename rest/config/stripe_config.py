"""Stripe configuration management - Open Source Stub."""

import logging
from typing import Dict

from pydantic import BaseModel

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StripeConfig(BaseModel):
    """Stripe configuration settings - Open Source Stub."""
    secret_key: str = ""
    publishable_key: str = ""
    webhook_signing_secret: str = ""
    plan_starter_price_id: str = ""
    plan_pro_price_id: str = ""
    plan_startup_price_id: str = ""
    mode: str = "disabled"

    @classmethod
    def from_env(cls) -> "StripeConfig":
        """Create stub Stripe configuration for open source."""
        logger.info(
            "Stripe configuration disabled - using open source version")
        return cls()

    def get_plan_price_ids(self) -> Dict[str, str]:
        r"""Get a dictionary of plan name to price ID mappings - stub
        implementation.
        """
        return {
            "starter": "",
            "pro": "",
            "startups": "",
        }


# Initialize global Stripe settings (stub)
stripe_config = StripeConfig.from_env()
