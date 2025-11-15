"""Event API endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.models.schemas import Event, EventCreate, EventUpdate
from app.services.event_service import EventService

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=List[Event], status_code=status.HTTP_200_OK)
async def get_events(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    venue_id: Optional[int] = Query(None, description="Filter by venue ID"),
    category: Optional[str] = Query(None, description="Filter by category"),
    db: Session = Depends(get_db)
):
    """Get all events with optional filtering."""
    events = EventService.get_events(
        db, skip=skip, limit=limit, venue_id=venue_id, category=category
    )
    return events


@router.get("/map", response_model=List[Event], status_code=status.HTTP_200_OK)
async def get_events_by_map_bounds(
    min_lat: float = Query(..., description="Minimum latitude (south boundary)", ge=-90, le=90),
    max_lat: float = Query(..., description="Maximum latitude (north boundary)", ge=-90, le=90),
    min_lon: float = Query(..., description="Minimum longitude (west boundary)", ge=-180, le=180),
    max_lon: float = Query(..., description="Maximum longitude (east boundary)", ge=-180, le=180),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """
    Get events within a geographic bounding box.
    
    Returns events whose venues are located within the specified map bounds.
    Requires all four boundary parameters (min_lat, max_lat, min_lon, max_lon).
    """
    # Validate bounds
    if min_lat >= max_lat:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="min_lat must be less than max_lat"
        )
    
    if min_lon >= max_lon:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="min_lon must be less than max_lon"
        )
    
    events = EventService.get_events_by_bounds(
        db,
        min_lat=min_lat,
        max_lat=max_lat,
        min_lon=min_lon,
        max_lon=max_lon,
        skip=skip,
        limit=limit
    )
    
    return events


@router.get("/{event_id}", response_model=Event, status_code=status.HTTP_200_OK)
async def get_event(
    event_id: int,
    db: Session = Depends(get_db)
):
    """Get an event by ID."""
    event = EventService.get_event(db, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with id {event_id} not found"
        )
    return event


@router.post("", response_model=Event, status_code=status.HTTP_201_CREATED)
async def create_event(
    event: EventCreate,
    db: Session = Depends(get_db)
):
    """Create a new event."""
    return EventService.create_event(db, event)


@router.put("/{event_id}", response_model=Event, status_code=status.HTTP_200_OK)
async def update_event(
    event_id: int,
    event_update: EventUpdate,
    db: Session = Depends(get_db)
):
    """Update an event."""
    event = EventService.update_event(db, event_id, event_update)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with id {event_id} not found"
        )
    return event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: int,
    db: Session = Depends(get_db)
):
    """Delete an event."""
    success = EventService.delete_event(db, event_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with id {event_id} not found"
        )
    return None

