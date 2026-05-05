"""Main FastAPI application"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from app.routers.simulations import router as simulations_router
from app.routers.allocations import router as allocations_router
from app.routers.events import router as events_router
from app.routers.timestep_logs import router as timestep_logs_router
from app.routers.analytics import router as analytics_router

# Initialize database
if settings.use_mongodb:
    # MongoDB initialization
    from app.mongo_db.connection import MongoDBConnection, MongoDBInitializer
    
    try:
        mongo_connection = MongoDBConnection()
        mongo_connection.connect()
        print("[OK] Connected to MongoDB")
        
        db = mongo_connection.get_database()
        MongoDBInitializer.initialize_collections(db)
        MongoDBInitializer.create_indexes(db)
        MongoDBInitializer.verify_setup(db)
        print("[OK] MongoDB initialized with collections and indexes")
    except Exception as e:
        print(f"[FAIL] MongoDB initialization failed: {e}")
        raise
else:
    # SQLite initialization (legacy)
    from app.models.base import Base
    from app.database.session import engine
    
    try:
        Base.metadata.create_all(bind=engine)
        print("[OK] SQLite database initialized")
    except Exception as e:
        print(f"[FAIL] SQLite initialization failed: {e}")
        pass  # Allow failure in testing environments

# Initialize FastAPI app
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    debug=settings.debug,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(simulations_router)
app.include_router(allocations_router)
app.include_router(events_router)
app.include_router(timestep_logs_router)
app.include_router(analytics_router)


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "CrisisGrid Backend Engine"}


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "CrisisGrid Backend Engine - Multi-agent Crisis Response System",
        "version": settings.api_version,
        "docs": "/docs",
        "endpoints": {
            "simulations": "/api/v1/simulations",
            "api_docs": "/docs",
            "openapi": "/openapi.json",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
