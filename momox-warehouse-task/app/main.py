import logging

from fastapi import FastAPI

from app.database import Base, engine
from app.routers import orders

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Warehouse Pick List Service",
    description="Microservice for generating warehouse pick lists at momox",
    version="0.1.0",
)

# Register routers
app.include_router(orders.router)


@app.get("/health")
def health_check():
    """Basic health check endpoint."""
    return {"status": "ok"}
