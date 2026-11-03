from fastapi import APIRouter

from codemind.database.analytics import AnalyticsRepository

router = APIRouter(
    prefix="/api/v1/analytics",
    tags=["Analytics"],
)


@router.get("")
def get_analytics():
    """Return usage statistics for the CodeMind API."""
    repo = AnalyticsRepository()
    return repo.summary()
