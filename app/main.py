"""FastAPI application entry point."""
from fastapi import FastAPI
from app.models.schemas import HealthResponse, Item

app = FastAPI(
    title="Eventify API",
    description="Eventify Backend API",
    version="1.0.0"
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to Eventify API"}


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint."""
    return HealthResponse(status="healthy", message="API is running")


@app.post("/items/")
async def create_item(item: Item):
    """Create item endpoint."""
    return {"item": item, "message": "Item created successfully"}
