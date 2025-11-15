"""Venue API endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.models.schemas import Venue, VenueCreate, VenueUpdate
from app.services.venue_service import VenueService

router = APIRouter(prefix="/venues", tags=["venues"])


@router.get("", response_model=List[Venue], status_code=status.HTTP_200_OK)
async def get_venues(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    neighborhood_id: Optional[int] = Query(None, description="Filter by neighborhood ID"),
    db: Session = Depends(get_db)
):
    """Get all venues with optional filtering by neighborhood."""
    venues = VenueService.get_venues(
        db, skip=skip, limit=limit, neighborhood_id=neighborhood_id
    )
    return venues


@router.get("/map", response_model=List[Venue], status_code=status.HTTP_200_OK)
async def get_venues_by_map_bounds(
    min_lat: float = Query(..., description="Minimum latitude (south boundary)", ge=-90, le=90),
    max_lat: float = Query(..., description="Maximum latitude (north boundary)", ge=-90, le=90),
    min_lon: float = Query(..., description="Minimum longitude (west boundary)", ge=-180, le=180),
    max_lon: float = Query(..., description="Maximum longitude (east boundary)", ge=-180, le=180),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """
    Get venues within a geographic bounding box.
    
    Returns venues located within the specified map bounds.
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
    
    venues = VenueService.get_venues_by_bounds(
        db,
        min_lat=min_lat,
        max_lat=max_lat,
        min_lon=min_lon,
        max_lon=max_lon,
        skip=skip,
        limit=limit
    )
    
    return venues


@router.get("/{venue_id}", response_model=Venue, status_code=status.HTTP_200_OK)
async def get_venue(
    venue_id: int,
    db: Session = Depends(get_db)
):
    """Get a venue by ID."""
    venue = VenueService.get_venue(db, venue_id)
    if not venue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Venue with id {venue_id} not found"
        )
    return venue


@router.post("", response_model=Venue, status_code=status.HTTP_201_CREATED)
async def create_venue(
    venue: VenueCreate,
    db: Session = Depends(get_db)
):
    """Create a new venue."""
    return VenueService.create_venue(db, venue)


@router.put("/{venue_id}", response_model=Venue, status_code=status.HTTP_200_OK)
async def update_venue(
    venue_id: int,
    venue_update: VenueUpdate,
    db: Session = Depends(get_db)
):
    """Update a venue."""
    venue = VenueService.update_venue(db, venue_id, venue_update)
    if not venue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Venue with id {venue_id} not found"
        )
    return venue


@router.delete("/{venue_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_venue(
    venue_id: int,
    db: Session = Depends(get_db)
):
    """Delete a venue."""
    success = VenueService.delete_venue(db, venue_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Venue with id {venue_id} not found"
        )
    return None

