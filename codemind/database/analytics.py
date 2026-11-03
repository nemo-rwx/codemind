from __future__ import annotations

from pathlib import Path

from codemind.database.connection import DEFAULT_DB_PATH, get_connection


class AnalyticsRepository:
    """Persist and query usage analytics events."""

    def __init__(self, db_path: Path = DEFAULT_DB_PATH):
        self.db_path = db_path

    def record(self, event: dict) -> None:
        """Insert one analytics event."""
        with get_connection(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO analytics_events (
                    event_type, client_ip, endpoint, method,
                    status_code, duration_ms, repository_path,
                    query, tool_iterations, error
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.get("event_type", "request"),
                    event.get("client_ip"),
                    event.get("endpoint", ""),
                    event.get("method", ""),
                    event.get("status_code"),
                    event.get("duration_ms"),
                    event.get("repository_path"),
                    event.get("query"),
                    event.get("tool_iterations"),
                    event.get("error"),
                ),
            )

    def summary(self) -> dict:
        """Return aggregate usage statistics."""
        with get_connection(self.db_path) as conn:
            total = conn.execute(
                "SELECT COUNT(*) AS n FROM analytics_events"
            ).fetchone()["n"]

            unique_ips = conn.execute(
                "SELECT COUNT(DISTINCT client_ip) AS n"
                " FROM analytics_events WHERE client_ip IS NOT NULL"
            ).fetchone()["n"]

            by_endpoint = [
                dict(r) for r in conn.execute(
                    "SELECT endpoint, COUNT(*) AS requests"
                    " FROM analytics_events GROUP BY endpoint ORDER BY requests DESC"
                ).fetchall()
            ]

            errors = conn.execute(
                "SELECT COUNT(*) AS n FROM analytics_events WHERE status_code >= 400"
            ).fetchone()["n"]

            avg_duration = conn.execute(
                "SELECT ROUND(AVG(duration_ms), 2) AS avg"
                " FROM analytics_events WHERE duration_ms IS NOT NULL"
            ).fetchone()["avg"]

            daily = [
                dict(r) for r in conn.execute(
                    "SELECT strftime('%Y-%m-%d', created_at) AS date,"
                    " COUNT(*) AS requests"
                    " FROM analytics_events GROUP BY date ORDER BY date DESC LIMIT 30"
                ).fetchall()
            ]

            top_queries = [
                dict(r) for r in conn.execute(
                    "SELECT query, COUNT(*) AS times"
                    " FROM analytics_events WHERE query IS NOT NULL"
                    " GROUP BY query ORDER BY times DESC LIMIT 10"
                ).fetchall()
            ]

        return {
            "total_requests": total,
            "unique_clients": unique_ips,
            "error_requests": errors,
            "avg_duration_ms": avg_duration,
            "requests_by_endpoint": by_endpoint,
            "requests_per_day": daily,
            "top_queries": top_queries,
        }
