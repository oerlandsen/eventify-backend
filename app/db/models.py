"""SQLAlchemy database models."""
from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, Time, ARRAY, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Neighborhood(Base):
    """Neighborhood database model."""
    __tablename__ = "neighborhoods"
    
    id = Column(Integer, primary_key=True, index=True)
    description = Column(Text, nullable=False)
    coordinates = Column(ARRAY(Float), nullable=False)  # [latitude, longitude]
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    venues = relationship("Venue", back_populates="neighborhood", cascade="all, delete-orphan")


class Venue(Base):
    """Venue database model."""
    __tablename__ = "venues"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    type = Column(String(50), nullable=False)  # Restaurant, Bar, Night club, etc.
    description = Column(Text, nullable=True)
    stars = Column(Float, nullable=True)  # Rating out of 10
    coordinates = Column(ARRAY(Float), nullable=False)  # [latitude, longitude]
    schedule = Column(Time, nullable=True)
    neighborhood_id = Column(Integer, ForeignKey("neighborhoods.id"), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    neighborhood = relationship("Neighborhood", back_populates="venues")
    events = relationship("Event", back_populates="venue", cascade="all, delete-orphan")


class Event(Base):
    """Event database model."""
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    venue_id = Column(Integer, ForeignKey("venues.id"), nullable=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    type = Column(String(50), nullable=True)  # Tour, Music, Outdoors, Festival
    category = Column(String(100), nullable=False)  # Sports/park, Rock/jazz/etc, Music/art/food
    keywords = Column(ARRAY(String), nullable=True)  # List of keywords
    description = Column(Text, nullable=True)
    price_range = Column(ARRAY(Float), nullable=True)  # [min_price, max_price]
    date = Column(String(50), nullable=False)  # Event date
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    venue = relationship("Venue", back_populates="events")

