from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, locations, work_orders
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(locations.router, prefix="/api/v1")
app.include_router(work_orders.router, prefix="/api/v1")


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Work Order API", "version": settings.app_version}


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}
