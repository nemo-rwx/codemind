from pydantic import BaseModel, Field


class RepositoryScanRequest(BaseModel):
    """Request model for repository scanning."""

    path: str = Field(
        ...,
        min_length=1,
        description="Absolute path of the repository to scan",
        examples=["C:/projects/my-java-project"],
    )
