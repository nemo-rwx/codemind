from pydantic import BaseModel, Field


class FileInfo(BaseModel):
    path: str
    extension: str
    language: str
    size_bytes: int


class RepositorySummary(BaseModel):
    root_path: str
    total_files: int = 0
    total_directories: int = 0
    total_size_bytes: int = 0
    language_counts: dict[str, int] = Field(default_factory=dict)
    files: list[FileInfo] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
