"""Event service layer."""
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.db.models import Event, Venue
from app.models.schemas import EventCreate, EventUpdate
from app.services.coordinate_filter import filter_by_coordinate_bounds


class EventService:
    """Service for event operations."""

    @staticmethod
    def get_event(db: Session, event_id: int) -> Optional[Event]:
        """Get an event by ID."""
        return db.query(Event).filter(Event.id == event_id).first()

    @staticmethod
    def get_events(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        venue_id: Optional[int] = None,
        category: Optional[str] = None
    ) -> List[Event]:
        """Get all events with optional filtering."""
        query = db.query(Event)
        
        if venue_id is not None:
            query = query.filter(Event.venue_id == venue_id)
        
        if category is not None:
            query = query.filter(Event.category == category)
        
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def create_event(db: Session, event: EventCreate) -> Event:
        """Create a new event."""
        db_event = Event(
            name=event.name,
            type=event.type,
            category=event.category,
            keywords=event.keywords,
            description=event.description,
            price_range=event.price_range,
            date=event.date,
            venue_id=event.venue_id
        )
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
        return db_event

    @staticmethod
    def update_event(
        db: Session,
        event_id: int,
        event_update: EventUpdate
    ) -> Optional[Event]:
        """Update an event."""
        db_event = db.query(Event).filter(Event.id == event_id).first()
        
        if not db_event:
            return None
        
        update_data = event_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_event, field, value)
        
        db.commit()
        db.refresh(db_event)
        return db_event

    @staticmethod
    def delete_event(db: Session, event_id: int) -> bool:
        """Delete an event."""
        db_event = db.query(Event).filter(Event.id == event_id).first()
        
        if not db_event:
            return False
        
        db.delete(db_event)
        db.commit()
        return True

    @staticmethod
    def get_events_by_bounds(
        db: Session,
        min_lat: float,
        max_lat: float,
        min_lon: float,
        max_lon: float,
        skip: int = 0,
        limit: int = 100
    ) -> List[Event]:
        """
        Get events within a geographic bounding box.
        
        Args:
            db: Database session
            min_lat: Minimum latitude (south boundary)
            max_lat: Maximum latitude (north boundary)
            min_lon: Minimum longitude (west boundary)
            max_lon: Maximum longitude (east boundary)
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of events with venues within the bounds
        """
        # Join Event with Venue and filter by coordinates
        query = db.query(Event).join(Venue, Event.venue_id == Venue.id)
        query = filter_by_coordinate_bounds(
            query, "venues", min_lat, max_lat, min_lon, max_lon
        )
        query = query.options(joinedload(Event.venue))
        
        return query.offset(skip).limit(limit).all()

