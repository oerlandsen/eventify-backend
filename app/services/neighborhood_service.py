"""Neighborhood service layer."""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.models import Neighborhood
from app.models.schemas import NeighborhoodCreate, NeighborhoodUpdate
from app.services.coordinate_filter import filter_by_polygon_bounds


class NeighborhoodService:
    """Service for neighborhood operations."""

    @staticmethod
    def get_neighborhood(db: Session, neighborhood_id: int) -> Optional[Neighborhood]:
        """Get a neighborhood by ID."""
        return db.query(Neighborhood).filter(Neighborhood.id == neighborhood_id).first()

    @staticmethod
    def get_neighborhoods(
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[Neighborhood]:
        """Get all neighborhoods with pagination."""
        return db.query(Neighborhood).offset(skip).limit(limit).all()

    @staticmethod
    def create_neighborhood(
        db: Session,
        neighborhood: NeighborhoodCreate
    ) -> Neighborhood:
        """Create a new neighborhood."""
        db_neighborhood = Neighborhood(
            description=neighborhood.description,
            coordinates=neighborhood.coordinates
        )
        db.add(db_neighborhood)
        db.commit()
        db.refresh(db_neighborhood)
        return db_neighborhood

    @staticmethod
    def update_neighborhood(
        db: Session,
        neighborhood_id: int,
        neighborhood_update: NeighborhoodUpdate
    ) -> Optional[Neighborhood]:
        """Update a neighborhood."""
        db_neighborhood = db.query(Neighborhood).filter(
            Neighborhood.id == neighborhood_id
        ).first()
        
        if not db_neighborhood:
            return None
        
        update_data = neighborhood_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_neighborhood, field, value)
        
        db.commit()
        db.refresh(db_neighborhood)
        return db_neighborhood

    @staticmethod
    def delete_neighborhood(db: Session, neighborhood_id: int) -> bool:
        """Delete a neighborhood."""
        db_neighborhood = db.query(Neighborhood).filter(
            Neighborhood.id == neighborhood_id
        ).first()
        
        if not db_neighborhood:
            return False
        
        db.delete(db_neighborhood)
        db.commit()
        return True

    @staticmethod
    def get_neighborhoods_by_bounds(
        db: Session,
        min_lat: float,
        max_lat: float,
        min_lon: float,
        max_lon: float,
        skip: int = 0,
        limit: int = 100
    ) -> List[Neighborhood]:
        """
        Get neighborhoods within a geographic bounding box.
        
        Note: Neighborhoods have multiple coordinate pairs (polygons).
        This filters neighborhoods where at least one coordinate pair intersects with the bounds.
        
        Args:
            db: Database session
            min_lat: Minimum latitude (south boundary)
            max_lat: Maximum latitude (north boundary)
            min_lon: Minimum longitude (west boundary)
            max_lon: Maximum longitude (east boundary)
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of neighborhoods with coordinates intersecting the bounds
        """
        query = db.query(Neighborhood)
        query = filter_by_polygon_bounds(
            query, "neighborhoods", min_lat, max_lat, min_lon, max_lon
        )
        
        return query.offset(skip).limit(limit).all()

