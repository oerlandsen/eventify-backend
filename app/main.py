"""FastAPI application entry point."""
import logging
from fastapi import FastAPI
from app.models.schemas import HealthResponse
from app.db.base import Base, engine
from app.config import settings
from app.db import models  # Import models to register them with Base
from app.api.router import api_router

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    description="Eventify Backend API - Events Microservice",
    version=settings.APP_VERSION
)

# Include API routers
app.include_router(api_router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    """Create database tables on startup."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        # Don't raise - allow app to start even if DB is not ready


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to Eventify API"}


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint with database connectivity check."""
    from sqlalchemy import text
    from app.db.base import SessionLocal
    
    try:
        # Check database connection
        db = SessionLocal()
        try:
            db.execute(text("SELECT 1"))
            db_status = "connected"
        except Exception as e:
            db_status = f"disconnected: {str(e)}"
        finally:
            db.close()
        
        if db_status == "connected":
            return HealthResponse(
                status="healthy",
                message="API is running and database is connected"
            )
        else:
            return HealthResponse(
                status="degraded",
                message=f"API is running but database is {db_status}"
            )
    except Exception as e:
        return HealthResponse(
            status="unhealthy",
            message=f"Health check failed: {str(e)}"
        )
