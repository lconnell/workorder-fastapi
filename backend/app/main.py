from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import auth, locations, work_orders
from app.core.config import settings
from app.utils.debug import debug_log_exception

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)


# Exception middleware to catch unhandled errors
@app.middleware("http")
async def catch_exceptions_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    try:
        return await call_next(request)
    except Exception as e:
        debug_log_exception(f"Unhandled exception in {request.method} {request.url}", e)

        # Return a proper JSON error response
        return JSONResponse(
            status_code=500,
            content={
                "detail": (
                    f"Internal server error: {str(e)}"
                    if settings.debug
                    else "Internal server error"
                )
            },
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
