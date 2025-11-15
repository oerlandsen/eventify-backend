"""Neighborhood API endpoints."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.models.schemas import (
    Neighborhood,
    NeighborhoodCreate,
    NeighborhoodUpdate
)
from app.services.neighborhood_service import NeighborhoodService

router = APIRouter(prefix="/neighborhoods", tags=["neighborhoods"])


@router.get("", response_model=List[Neighborhood], status_code=status.HTTP_200_OK)
async def get_neighborhoods(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """Get all neighborhoods with pagination."""
    neighborhoods = NeighborhoodService.get_neighborhoods(db, skip=skip, limit=limit)
    return neighborhoods


@router.get("/{neighborhood_id}", response_model=Neighborhood, status_code=status.HTTP_200_OK)
async def get_neighborhood(
    neighborhood_id: int,
    db: Session = Depends(get_db)
):
    """Get a neighborhood by ID."""
    neighborhood = NeighborhoodService.get_neighborhood(db, neighborhood_id)
    if not neighborhood:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Neighborhood with id {neighborhood_id} not found"
        )
    return neighborhood


@router.post("", response_model=Neighborhood, status_code=status.HTTP_201_CREATED)
async def create_neighborhood(
    neighborhood: NeighborhoodCreate,
    db: Session = Depends(get_db)
):
    """Create a new neighborhood."""
    return NeighborhoodService.create_neighborhood(db, neighborhood)


@router.put("/{neighborhood_id}", response_model=Neighborhood, status_code=status.HTTP_200_OK)
async def update_neighborhood(
    neighborhood_id: int,
    neighborhood_update: NeighborhoodUpdate,
    db: Session = Depends(get_db)
):
    """Update a neighborhood."""
    neighborhood = NeighborhoodService.update_neighborhood(
        db, neighborhood_id, neighborhood_update
    )
    if not neighborhood:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Neighborhood with id {neighborhood_id} not found"
        )
    return neighborhood


@router.delete("/{neighborhood_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_neighborhood(
    neighborhood_id: int,
    db: Session = Depends(get_db)
):
    """Delete a neighborhood."""
    success = NeighborhoodService.delete_neighborhood(db, neighborhood_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Neighborhood with id {neighborhood_id} not found"
        )
    return None

