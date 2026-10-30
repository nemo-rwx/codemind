from fastapi.testclient import TestClient

from codemind.api.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_scan_repository_success(tmp_path):
    # Arrange: create a temporary repository
    (tmp_path / "main.py").write_text(
        "print('Hello CodeMind')",
        encoding="utf-8",
    )

    # Act: call the API
    response = client.post(
        "/api/v1/repositories/scan",
        json={"path": str(tmp_path)},
    )

    # Assert: verify the response
    assert response.status_code == 200

    data = response.json()

    assert data["total_files"] == 1
    assert data["language_counts"]["Python"] == 1


def test_scan_repository_not_found():
    response = client.post(
        "/api/v1/repositories/scan",
        json={"path": "Z:/this-folder-does-not-exist"},
    )

    assert response.status_code == 404
