import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from rest.routers.explore import ExploreRouter

try:
    from rest.routers.ee.verify import VerifyRouter
except ImportError:
    from rest.routers.verify import VerifyRouter

from rest.routers.internal import InternalRouter

version = "0.1.3"


class App:
    r"""The TraceRoot API app."""

    def __init__(self):
        # Initialize rate limiter
        self.limiter = Limiter(key_func=get_remote_address)

        self.app = FastAPI(title="TraceRoot API", version=version)

        # Add rate limit exception handler
        self.app.state.limiter = self.limiter
        self.app.add_exception_handler(
            RateLimitExceeded,
            _rate_limit_exceeded_handler,
        )
        self.local_mode = os.getenv("REST_LOCAL_MODE", "false").lower() == "true"

        # Add CORS middleware
        self.add_middleware()

        self.explore_router = ExploreRouter(self.local_mode, self.limiter)
        self.app.include_router(
            self.explore_router.router,
            prefix="/v1/explore",
            tags=["explore"],
        )

        # Add verify router for SDK verification
        self.verify_router = VerifyRouter(self.limiter)
        self.app.include_router(
            self.verify_router.router,
            prefix="/v1/verify",
            tags=["verify"],
        )

        # Add internal router for OTLP usage tracking
        self.internal_router = InternalRouter()
        self.app.include_router(
            self.internal_router.router,
            prefix="/v1/internal",
            tags=["internal"],
        )

    def add_middleware(self):
        main_domain = os.getenv("MAIN_DOMAIN")
        allow_origins = [
            f"https://{main_domain}",
            f"https://api.{main_domain}",
            "http://localhost:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001",
        ]
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=allow_origins,
            allow_credentials=True,
            allow_methods=["GET",
                           "POST",
                           "PUT",
                           "DELETE",
                           "OPTIONS",
                           "PATCH"],
            allow_headers=["*"],
        )
