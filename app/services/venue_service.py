"""Venue service layer."""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.models import Venue
from app.models.schemas import VenueCreate, VenueUpdate
from app.services.coordinate_filter import filter_by_coordinate_bounds


class VenueService:
    """Service for venue operations."""

    @staticmethod
    def get_venue(db: Session, venue_id: int) -> Optional[Venue]:
        """Get a venue by ID."""
        return db.query(Venue).filter(Venue.id == venue_id).first()

    @staticmethod
    def get_venues(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        neighborhood_id: Optional[int] = None
    ) -> List[Venue]:
        """Get all venues with optional filtering by neighborhood."""
        query = db.query(Venue)
        
        if neighborhood_id is not None:
            query = query.filter(Venue.neighborhood_id == neighborhood_id)
        
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def create_venue(db: Session, venue: VenueCreate) -> Venue:
        """Create a new venue."""
        db_venue = Venue(
            name=venue.name,
            type=venue.type,
            description=venue.description,
            stars=venue.stars,
            coordinates=venue.coordinates,
            schedule=venue.schedule,
            neighborhood_id=venue.neighborhood_id
        )
        db.add(db_venue)
        db.commit()
        db.refresh(db_venue)
        return db_venue

    @staticmethod
    def update_venue(
        db: Session,
        venue_id: int,
        venue_update: VenueUpdate
    ) -> Optional[Venue]:
        """Update a venue."""
        db_venue = db.query(Venue).filter(Venue.id == venue_id).first()
        
        if not db_venue:
            return None
        
        update_data = venue_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_venue, field, value)
        
        db.commit()
        db.refresh(db_venue)
        return db_venue

    @staticmethod
    def delete_venue(db: Session, venue_id: int) -> bool:
        """Delete a venue."""
        db_venue = db.query(Venue).filter(Venue.id == venue_id).first()
        
        if not db_venue:
            return False
        
        db.delete(db_venue)
        db.commit()
        return True
    
    @staticmethod
    def get_all_types_of_venues(neighborhood_id: int, db: Session) -> List[str]:
        """Get all types of venues."""
        results = db.query(Venue.type).filter(Venue.neighborhood_id == neighborhood_id).distinct().all()
        return [row[0] for row in results if row[0] is not None]

    @staticmethod
    def get_venues_by_bounds(
        db: Session,
        min_lat: float,
        max_lat: float,
        min_lon: float,
        max_lon: float,
        skip: int = 0,
        limit: int = 100
    ) -> List[Venue]:
        """
        Get venues within a geographic bounding box.
        
        Args:
            db: Database session
            min_lat: Minimum latitude (south boundary)
            max_lat: Maximum latitude (north boundary)
            min_lon: Minimum longitude (west boundary)
            max_lon: Maximum longitude (east boundary)
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of venues within the bounds
        """
        query = db.query(Venue)
        query = filter_by_coordinate_bounds(
            query, "venues", min_lat, max_lat, min_lon, max_lon
        )
        
        return query.offset(skip).limit(limit).all()

