from codemind.scanner.service import RepositoryScanner


def get_repository_scanner() -> RepositoryScanner:
    """Provide a repository scanner instance."""
    return RepositoryScanner()
