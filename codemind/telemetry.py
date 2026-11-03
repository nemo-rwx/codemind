from __future__ import annotations

import hashlib
import os
import platform
import uuid
from pathlib import Path

POSTHOG_API_KEY = "phc_qh6TUi6VcpsLBiE3GfTdSKRpii3mpvwSgGVQ6tKkGrXr"
POSTHOG_HOST = "https://us.i.posthog.com"
INSTALL_ID_PATH = Path.home() / ".codemind" / "install_id"


def _is_enabled() -> bool:
    return os.getenv("CODEMIND_TELEMETRY", "on").lower() not in ("off", "0", "false")


def _get_install_id() -> str:
    """Return a stable anonymous install ID, creating one if needed."""
    try:
        INSTALL_ID_PATH.parent.mkdir(parents=True, exist_ok=True)
        if INSTALL_ID_PATH.exists():
            return INSTALL_ID_PATH.read_text().strip()
        install_id = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()[:16]
        INSTALL_ID_PATH.write_text(install_id)
        return install_id
    except Exception:
        return "unknown"


def capture_ask(
    success: bool,
    iterations: int,
    query_length: int,
    error: str | None = None,
) -> None:
    """Fire a codemind_ask event to PostHog. Never raises."""
    if not _is_enabled():
        return
    try:
        import posthog
        posthog.project_api_key = POSTHOG_API_KEY
        posthog.host = POSTHOG_HOST
        posthog.capture(
            distinct_id=_get_install_id(),
            event="codemind_ask",
            properties={
                "success": success,
                "iterations": iterations,
                "query_length": query_length,
                "error": error,
                "python_version": platform.python_version(),
                "os": platform.system(),
            },
        )
        posthog.shutdown()
    except Exception:
        pass
