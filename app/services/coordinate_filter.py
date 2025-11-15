"""Utility functions for filtering by geographic coordinates."""
from typing import TypeVar, Generic
from sqlalchemy.orm import Query
from sqlalchemy import and_, text

# Generic type for SQLAlchemy models
ModelType = TypeVar('ModelType')


def filter_by_coordinate_bounds(
    query: Query,
    table_name: str,
    min_lat: float,
    max_lat: float,
    min_lon: float,
    max_lon: float
) -> Query:
    """
    Apply coordinate bounds filtering to a SQLAlchemy query.
    
    For single coordinate pairs (venues, events via venues).
    PostgreSQL arrays are 1-indexed: coordinates[1] = lat, coordinates[2] = lon
    
    Args:
        query: SQLAlchemy query object
        table_name: Name of the table containing the coordinates column
        min_lat: Minimum latitude (south boundary)
        max_lat: Maximum latitude (north boundary)
        min_lon: Minimum longitude (west boundary)
        max_lon: Maximum longitude (east boundary)
    
    Returns:
        Query with coordinate bounds filtering applied
    """
    return query.filter(
        and_(
            text(f"{table_name}.coordinates[1] >= :min_lat"),
            text(f"{table_name}.coordinates[1] <= :max_lat"),
            text(f"{table_name}.coordinates[2] >= :min_lon"),
            text(f"{table_name}.coordinates[2] <= :max_lon")
        )
    ).params(min_lat=min_lat, max_lat=max_lat, min_lon=min_lon, max_lon=max_lon)


def filter_by_polygon_bounds(
    query: Query,
    table_name: str,
    min_lat: float,
    max_lat: float,
    min_lon: float,
    max_lon: float
) -> Query:
    """
    Apply coordinate bounds filtering to a SQLAlchemy query for polygon coordinates.
    
    For neighborhoods with multiple coordinate pairs (2D arrays).
    Checks if ANY coordinate pair in the polygon intersects with the bounding box.
    
    PostgreSQL 2D arrays: coordinates[i][1] = lat, coordinates[i][2] = lon
    Uses generate_subscripts to iterate through each coordinate pair in the polygon.
    
    Args:
        query: SQLAlchemy query object
        table_name: Name of the table containing the coordinates column
        min_lat: Minimum latitude (south boundary)
        max_lat: Maximum latitude (north boundary)
        min_lon: Minimum longitude (west boundary)
        max_lon: Maximum longitude (east boundary)
    
    Returns:
        Query with coordinate bounds filtering applied
    """
    # Check if any coordinate pair in the polygon is within the bounds
    # Using EXISTS with generate_subscripts to iterate through each coordinate pair
    # For 2D array: coordinates[i] gives the i-th coordinate pair {lat, lon}
    # coordinates[i][1] gives lat, coordinates[i][2] gives lon
    return query.filter(
        text("""
            EXISTS (
                SELECT 1 
                FROM generate_subscripts({table_name}.coordinates, 1) AS i
                WHERE {table_name}.coordinates[i][1] >= :min_lat 
                  AND {table_name}.coordinates[i][1] <= :max_lat
                  AND {table_name}.coordinates[i][2] >= :min_lon
                  AND {table_name}.coordinates[i][2] <= :max_lon
            )
        """.format(table_name=table_name))
    ).params(min_lat=min_lat, max_lat=max_lat, min_lon=min_lon, max_lon=max_lon)

