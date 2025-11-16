"""Search service for filtering venues and events."""
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session, Query
from app.db.models import Venue, Event
from app.services.coordinate_filter import filter_by_coordinate_bounds


# Constants
NO_MATCHING_VENUES_ID = -1  # Used as impossible condition when no venues match


class ReturnType(str, Enum):
    """Enum for search return type."""
    BOTH = "both"
    EVENTS = "events"
    VENUES = "venues"


@dataclass
class SearchFilters:
    """Data class for search filter parameters."""
    venue_type: Optional[str] = None
    event_type: Optional[str] = None
    event_category: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    min_lat: Optional[float] = None
    max_lat: Optional[float] = None
    min_lon: Optional[float] = None
    max_lon: Optional[float] = None
    skip: int = 0
    limit: int = 100
    return_type: ReturnType = ReturnType.BOTH
    
    def has_event_filters(self) -> bool:
        """Check if any event filters are applied."""
        return any([self.event_type, self.event_category, self.start_date])
    
    def has_venue_filters(self) -> bool:
        """Check if any venue filters are applied."""
        return self.venue_type is not None
    
    def has_coordinate_bounds(self) -> bool:
        """Check if coordinate bounds are provided."""
        return all([self.min_lat, self.max_lat, self.min_lon, self.max_lon])


class SearchService:
    """Service for searching and filtering venues and events."""
    
    def __init__(self, db: Session):
        """
        Initialize SearchService with database session.
        
        Args:
            db: Database session
        """
        self.db = db

    def search_by_filters(self, filters: SearchFilters) -> Dict[str, Any]:
        """
        Search venues and events by various filters.
        
        Filters can be combined with AND logic:
        - venue_type + event_type: Venues of that type that have events of that type
        - venue_type + event_category: Venues of that type that have events of that category
        - event_type + event_category: Events matching both, venues that have those events
        - start_date: Filter events by single date (format: 'YYYY-MM-DD')
        - start_date + end_date: Filter events by date range (inclusive)
        - All filters: Venues matching venue_type that have events matching event_type, event_category, and date range
        
        Args:
            filters: SearchFilters object containing all filter parameters
            
        Returns:
            Dictionary with 'venues' and 'events' lists, plus metadata
        """
        # Build event query with filters
        event_query = self._build_event_query(filters)
        
        # Determine which venues to include based on event filters
        venue_query = self._build_venue_query(
            filters, event_query, filters.has_event_filters()
        )
        
        # Get filtered venues (only if return_type includes venues)
        venues: List[Venue] = []
        events: List[Event] = []
        
        
        if filters.return_type == ReturnType.BOTH:
            venues = venue_query.offset(filters.skip).limit(filters.limit).all()
            events = self._get_events_for_venues(
                venues, filters, filters.has_event_filters()
            )
        elif filters.return_type == ReturnType.EVENTS:
            events = event_query.offset(filters.skip).limit(filters.limit).all()
        elif filters.return_type == ReturnType.VENUES:
            venues = venue_query.offset(filters.skip).limit(filters.limit).all()
        
        return {
            "venues": venues,
            "events": events,
            "meta": {
                "total_venues": len(venues),
                "total_events": len(events),
                "filters_applied": {
                    "venue_type": filters.venue_type,
                    "event_type": filters.event_type,
                    "event_category": filters.event_category,
                    "start_date": filters.start_date,
                    "end_date": filters.end_date,
                    "return_type": filters.return_type.value
                }
            }
        }

    def _build_event_query(self, filters: SearchFilters) -> Query:
        """
        Build event query with all event filters applied.
        
        Args:
            filters: SearchFilters object
            
        Returns:
            SQLAlchemy query for events with filters applied
        """
        event_query = self.db.query(Event)
        event_query = self._apply_event_filters(event_query, filters)
        return event_query

    def _apply_event_filters(self, event_query: Query, filters: SearchFilters) -> Query:
        """
        Apply event filters to a query.
        
        Args:
            event_query: Base event query
            filters: SearchFilters object
            
        Returns:
            Query with event filters applied
        """
        if filters.event_type is not None:
            event_query = event_query.filter(Event.type == filters.event_type)
        
        if filters.event_category is not None:
            event_query = event_query.filter(Event.category == filters.event_category)
        
        event_query = self._apply_date_filter(event_query, filters)
        
        return event_query

    def _apply_date_filter(self, event_query: Query, filters: SearchFilters) -> Query:
        """
        Apply date filter to event query (single date or date range).
        
        Args:
            event_query: Event query to filter
            filters: SearchFilters object
            
        Returns:
            Query with date filter applied
        """
        if filters.start_date is None:
            return event_query
        
        if filters.end_date is not None:
            # Date range: filter events between start_date and end_date (inclusive)
            event_query = event_query.filter(
                Event.date >= filters.start_date,
                Event.date <= filters.end_date
            )
        else:
            # Single date: filter events on that exact date
            event_query = event_query.filter(Event.date == filters.start_date)
        
        return event_query

    def _build_venue_query(
        self,
        filters: SearchFilters,
        event_query: Query,
        has_event_filters: bool
    ) -> Query:
        """
        Build venue query based on filters and matching events.
        
        Args:
            filters: SearchFilters object
            event_query: Event query with filters applied
            has_event_filters: Whether event filters were applied
            
        Returns:
            SQLAlchemy query for venues with filters applied
        """
        venue_query = self.db.query(Venue)
        
        # If event filters are applied, restrict venues to those with matching events
        if has_event_filters:
            venue_query = self._restrict_venues_to_matching_events(
                venue_query, event_query
            )
        
        # Apply venue-specific filters
        venue_query = self._apply_venue_filters(venue_query, filters)
        
        return venue_query

    def _restrict_venues_to_matching_events(
        self,
        venue_query: Query,
        event_query: Query
    ) -> Query:
        """
        Restrict venue query to only venues that have matching events.
        
        Args:
            venue_query: Base venue query
            event_query: Event query with filters applied
            
        Returns:
            Venue query restricted to venues with matching events
        """
        matching_events = event_query.all()
        
        if not matching_events:
            # No matching events, so no venues
            return venue_query.filter(Venue.id == NO_MATCHING_VENUES_ID)
        
        venue_ids = self._extract_venue_ids_from_events(matching_events)
        
        if not venue_ids:
            # No venues have matching events
            return venue_query.filter(Venue.id == NO_MATCHING_VENUES_ID)
        
        return venue_query.filter(Venue.id.in_(venue_ids))

    def _extract_venue_ids_from_events(self, events: List[Event]) -> List[int]:
        """
        Extract unique venue IDs from events.
        
        Args:
            events: List of event objects
            
        Returns:
            List of unique venue IDs (excluding None)
        """
        return list(set([
            event.venue_id for event in events
            if event.venue_id is not None
        ]))

    def _apply_venue_filters(self, venue_query: Query, filters: SearchFilters) -> Query:
        """
        Apply venue-specific filters to venue query.
        
        Args:
            venue_query: Base venue query
            filters: SearchFilters object
            
        Returns:
            Query with venue filters applied
        """
        if filters.venue_type is not None:
            venue_query = venue_query.filter(Venue.venue_type == filters.venue_type)
        
        # Apply coordinate bounds if provided
        if filters.has_coordinate_bounds():
            venue_query = filter_by_coordinate_bounds(
                venue_query,
                "venues",
                filters.min_lat,
                filters.max_lat,
                filters.min_lon,
                filters.max_lon
            )
        
        return venue_query

    def _get_events_for_venues(
        self,
        venues: List[Venue],
        filters: SearchFilters,
        has_event_filters: bool
    ) -> List[Event]:
        """
        Get events for the filtered venues, applying event filters if needed.
        
        Args:
            venues: List of filtered venues
            filters: SearchFilters object
            has_event_filters: Whether event filters were applied
            
        Returns:
            List of events matching the criteria
        """
        if not venues:
            return []
        
        venue_ids = [venue.id for venue in venues]
        
        if not has_event_filters:
            # No event filters: return all events for these venues
            return self.db.query(Event).filter(Event.venue_id.in_(venue_ids)).all()
        
        # Apply event filters and restrict to venues
        event_query = self.db.query(Event)
        event_query = self._apply_event_filters(event_query, filters)
        return event_query.filter(Event.venue_id.in_(venue_ids)).all()
