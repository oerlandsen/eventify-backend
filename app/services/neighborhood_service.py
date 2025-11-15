"""Neighborhood service layer."""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.models import Neighborhood
from app.models.schemas import NeighborhoodCreate, NeighborhoodUpdate


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

