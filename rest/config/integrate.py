from pydantic import BaseModel, Field

from rest.typing import ResourceType, TokenResource


class IntegrateRequest(BaseModel):
    """Request model for integrating a token resource."""
    token_resource: TokenResource


class IntegrateResponse(BaseModel):
    """Response model for integrate operations."""
    success: bool
    token: str | None = None
    error: str | None = None


class DeleteIntegrateRequest(BaseModel):
    """Request model for deleting a integration."""
    resource_type: str


class DeleteIntegrateResponse(BaseModel):
    """Response model for delete integrate operations."""
    success: bool
    error: str | None = None


class GetIntegrateRequest(BaseModel):
    """Request model for getting a integration token."""
    user_secret: str
    resource_type: ResourceType = Field(alias="resourceType")

    class Config:
        populate_by_name = True


class GetIntegrateResponse(BaseModel):
    """Response model for get integrate operations."""
    success: bool
    token: str | None = None
    error: str | None = None
