from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from datetime import datetime
from routes.v1.karma.main import router as karma_router
from routes import balance, redeem, policy
from routes.karma import router as karma_api_router  # New karma API router
from routes.rnanubandhan import router as rnanubandhan_router  # Rnanubandhan API router
from routes.agami import router as agami_router  # Agami Karma API router
# from routes import user, admin  # These modules don't exist yet
from database import close_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown
    try:
        close_client()
    except Exception:
        # Avoid raising during shutdown
        pass

app = FastAPI(
    title="KarmaChain v2 (Dual-Ledger)",
    description="A modular, portable karma tracking system for multi-department integration",
    version="1.0.0",
    lifespan=lifespan
)

# Consistent error response handlers

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    detail = getattr(exc, "detail", None)
    message = detail if isinstance(detail, str) else (
        detail.get("error") if isinstance(detail, dict) and isinstance(detail.get("error"), str) else "Request error"
    )
    payload = {
        "status": "error",
        "error": {
            "code": exc.status_code,
            "message": message
        },
        "path": request.url.path,
        "timestamp": datetime.utcnow().isoformat()
    }
    if isinstance(detail, dict):
        payload["details"] = detail
    return JSONResponse(status_code=exc.status_code, content=payload)

@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "error": {
                "code": 422,
                "message": "Validation failed"
            },
            "path": request.url.path,
            "timestamp": datetime.utcnow().isoformat(),
            "details": exc.errors()
        }
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "error": {
                "code": 500,
                "message": "Internal server error"
            },
            "path": request.url.path,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Configure CORS for cross-domain requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the versioned karma router
app.include_router(karma_router, prefix="/v1")

# Include the new karma API router
app.include_router(karma_api_router, prefix="/api/v1")

# Include Rnanubandhan API router
app.include_router(rnanubandhan_router, tags=["Rnanubandhan API"])

# Include Agami Karma API router
app.include_router(agami_router, tags=["Agami Karma API"])

# Include legacy routes (these will be migrated to versioned routes in future)
app.include_router(balance.router, tags=["Wallet Operations"])
app.include_router(redeem.router, tags=["Wallet Operations"])
app.include_router(policy.router, tags=["Wallet Operations"])
# app.include_router(user.router)  # Module doesn't exist yet
# app.include_router(admin.router)  # Module doesn't exist yet