import os
from pathlib import Path

from codemind.scanner.language_detector import detect_language
from codemind.scanner.models import FileInfo, RepositorySummary

IGNORED_DIRECTORIES = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    ".idea",
    ".pytest_cache",
    ".mypy_cache",
}


class RepositoryScanner:
    def scan(self, root_path: Path) -> RepositorySummary:
        """Scan a repository and collect basic file metadata."""
        root_path = root_path.expanduser().resolve()

        if not root_path.exists():
            raise FileNotFoundError(f"Repository not found: {root_path}")
        if not root_path.is_dir():
            raise NotADirectoryError(f"Expected a directory: {root_path}")

        summary = RepositorySummary(root_path=str(root_path))

        for current_root, directories, filenames in os.walk(
            root_path,
            topdown=True,
            followlinks=False,
        ):
            current = Path(current_root)
            directories[:] = [
                directory
                for directory in directories
                if directory not in IGNORED_DIRECTORIES
                and not (current / directory).is_symlink()
            ]
            summary.total_directories += len(directories)

            for filename in filenames:
                file_path = current / filename
                if file_path.is_symlink():
                    continue

                try:
                    if not file_path.is_file():
                        continue

                    size_bytes = file_path.stat().st_size
                    relative_path = file_path.relative_to(root_path)

                    info = FileInfo(
                        path=relative_path.as_posix(),
                        extension=file_path.suffix.lower(),
                        language=detect_language(file_path),
                        size_bytes=size_bytes,
                    )
                    summary.files.append(info)
                    summary.total_files += 1
                    summary.total_size_bytes += size_bytes
                    summary.language_counts[info.language] = (
                        summary.language_counts.get(info.language, 0) + 1
                    )
                except OSError as error:
                    summary.errors.append(f"{file_path}: {error}")

        return summary
