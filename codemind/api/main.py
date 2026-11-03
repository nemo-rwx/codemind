from contextlib import asynccontextmanager

from fastapi import FastAPI

from codemind.api.middleware import AnalyticsMiddleware
from codemind.api.routes.analytics import router as analytics_router
from codemind.api.routes.repositories import router as repository_router
from codemind.database.schema import initialize_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources on startup."""
    initialize_database()
    yield


app = FastAPI(
    title="CodeMind API",
    description="Agentic AI-powered Codebase Intelligence Assistant",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
def health_check():
    """Check whether the CodeMind API is running."""
    return {
        "status": "healthy",
        "service": "CodeMind API",
    }


app.add_middleware(AnalyticsMiddleware)
app.include_router(repository_router)
app.include_router(analytics_router)
