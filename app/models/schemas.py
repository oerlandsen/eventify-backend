"""Pydantic schemas for request/response models."""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime, time


class HealthResponse(BaseModel):
    """Health check response schema."""
    status: str
    message: str


# Neighborhood Schemas
class NeighborhoodBase(BaseModel):
    """Base neighborhood schema."""
    description: str
    coordinates: List[List[float]] = Field(..., description="Array of coordinate pairs [[lat, lon], [lat, lon], ...]")


class NeighborhoodCreate(NeighborhoodBase):
    """Schema for creating a neighborhood."""
    pass


class NeighborhoodUpdate(BaseModel):
    """Schema for updating a neighborhood."""
    description: Optional[str] = None
    coordinates: Optional[List[List[float]]] = None


class Neighborhood(NeighborhoodBase):
    """Neighborhood response schema."""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Venue Schemas
class VenueBase(BaseModel):
    """Base venue schema."""
    name: str = Field(..., max_length=255)
    type: str = Field(..., max_length=50)
    description: Optional[str] = None
    stars: Optional[float] = Field(None, ge=0, le=10, description="Rating out of 10")
    coordinates: List[float] = Field(..., min_items=2, max_items=2, description="[latitude, longitude]")
    schedule: Optional[time] = None
    neighborhood_id: Optional[int] = None


class VenueCreate(VenueBase):
    """Schema for creating a venue."""
    pass


class VenueUpdate(BaseModel):
    """Schema for updating a venue."""
    name: Optional[str] = Field(None, max_length=255)
    type: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    stars: Optional[float] = Field(None, ge=0, le=10)
    coordinates: Optional[List[float]] = None
    schedule: Optional[time] = None
    neighborhood_id: Optional[int] = None


class Venue(VenueBase):
    """Venue response schema."""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Event Schemas
class EventBase(BaseModel):
    """Base event schema."""
    name: str = Field(..., max_length=255)
    type: Optional[str] = Field(None, max_length=50)
    category: str = Field(..., max_length=100)
    keywords: Optional[List[str]] = None
    description: Optional[str] = None
    price_range: Optional[List[float]] = Field(None, min_items=2, max_items=2, description="[min_price, max_price]")
    date: str = Field(..., max_length=50)
    venue_id: Optional[int] = None
    
    @field_validator('price_range', mode='before')
    @classmethod
    def convert_empty_price_range_to_none(cls, v):
        """Convert empty arrays to None for price_range."""
        if isinstance(v, list) and len(v) == 0:
            return None
        return v
    
    @field_validator('keywords', mode='before')
    @classmethod
    def convert_empty_keywords_to_none(cls, v):
        """Convert empty arrays to None for keywords."""
        if isinstance(v, list) and len(v) == 0:
            return None
        return v


class EventCreate(EventBase):
    """Schema for creating an event."""
    pass


class EventUpdate(BaseModel):
    """Schema for updating an event."""
    name: Optional[str] = Field(None, max_length=255)
    type: Optional[str] = Field(None, max_length=50)
    category: Optional[str] = Field(None, max_length=100)
    keywords: Optional[List[str]] = None
    description: Optional[str] = None
    price_range: Optional[List[float]] = None
    date: Optional[str] = Field(None, max_length=50)
    venue_id: Optional[int] = None


class Event(EventBase):
    """Event response schema."""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
