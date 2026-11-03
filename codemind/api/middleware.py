from __future__ import annotations

import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from codemind.database.analytics import AnalyticsRepository


class AnalyticsMiddleware(BaseHTTPMiddleware):
    """Record every HTTP request as an analytics event."""

    def __init__(self, app, analytics: AnalyticsRepository | None = None):
        super().__init__(app)
        self.analytics = analytics or AnalyticsRepository()

    async def dispatch(self, request: Request, call_next):
        start = time.monotonic()
        error_detail = None

        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as exc:
            status_code = 500
            error_detail = str(exc)
            raise
        finally:
            duration_ms = round((time.monotonic() - start) * 1000, 2)
            client_ip = request.client.host if request.client else None

            try:
                self.analytics.record({
                    "event_type": "request",
                    "client_ip": client_ip,
                    "endpoint": request.url.path,
                    "method": request.method,
                    "status_code": status_code,
                    "duration_ms": duration_ms,
                    "error": error_detail,
                })
            except Exception:
                pass  # never let analytics break the response

        return response
