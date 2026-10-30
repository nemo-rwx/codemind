from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException

from codemind.api.dependencies import get_repository_scanner
from codemind.api.schemas.repository import RepositoryScanRequest
from codemind.scanner.models import RepositorySummary
from codemind.scanner.service import RepositoryScanner

router = APIRouter(
    prefix="/api/v1/repositories",
    tags=["Repositories"],
)


@router.post(
    "/scan",
    response_model=RepositorySummary,
)
def scan_repository(
    request: RepositoryScanRequest,
    scanner: RepositoryScanner = Depends(get_repository_scanner),
):
    """Scan a repository and return its summary."""

    try:
        result = scanner.scan(Path(request.path))
        return result

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error

    except NotADirectoryError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error
