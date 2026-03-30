from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.redteam import router as redteam_router  # We'll create this next

app = FastAPI(
    title="RTK-1 — Claude Orchestrated AI Red Teaming API",
    description="Production-grade defensive red-teaming toolkit (Claude + LangGraph + PyRIT/Garak)",
    version="0.1.0",
    docs_url="/docs",           # Recruiters love live OpenAPI docs
    redoc_url="/redoc",
)

# Security middleware (CORS for now — we'll add mTLS + rate limiting later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # Tighten this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all red-team routes
app.include_router(redteam_router, prefix="/api/v1")

@app.get("/health")
async def health():
    """Simple health check — proves the API is running with Claude orchestration."""
    return {
        "status": "healthy",
        "orchestrator": "Claude 4 + LangGraph",
        "version": "0.1.0",
        "settings_loaded": bool(settings.anthropic_api_key),
    }

# Optional: root endpoint for quick testing
@app.get("/")
async def root():
    return {
        "message": "🚀 RTK-1 is live! Try /api/v1/redteam/crescendo or /docs",
        "docs": "/docs",
    }