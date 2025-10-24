from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.v1.karma.main import router as karma_router
from routes import balance, redeem, policy
from routes.karma import router as karma_api_router  # New karma API router
# from routes import user, admin  # These modules don't exist yet

app = FastAPI(
    title="KarmaChain v2 (Dual-Ledger)",
    description="A modular, portable karma tracking system for multi-department integration",
    version="1.0.0"
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

# Include legacy routes (these will be migrated to versioned routes in future)
app.include_router(balance.router, tags=["Wallet Operations"])
app.include_router(redeem.router, tags=["Wallet Operations"])
app.include_router(policy.router, tags=["Wallet Operations"])
# app.include_router(user.router)  # Module doesn't exist yet
# app.include_router(admin.router)  # Module doesn't exist yet