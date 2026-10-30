from fastapi import FastAPI

from codemind.api.routes.repositories import router as repository_router

app = FastAPI(
    title="CodeMind API",
    description="Agentic AI-powered Codebase Intelligence Assistant",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    """Check whether the CodeMind API is running."""
    return {
        "status": "healthy",
        "service": "CodeMind API",
    }


app.include_router(repository_router)
