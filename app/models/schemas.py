"""Pydantic schemas for request/response models."""
from pydantic import BaseModel
from typing import Optional


class HealthResponse(BaseModel):
    """Health check response schema."""
    status: str
    message: str


class Item(BaseModel):
    """Item schema."""
    name: str
    description: Optional[str] = None
    price: float

