# Backend/tests/test_day1_integration.py

from fastapi.testclient import TestClient
from Backend.app.main import app

client = TestClient(app)


def test_cors_preflight_allows_frontend_origin():
    response = client.options(
        "/api/secondhand/",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code in (200, 204)
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"


def test_global_validation_exception_handler():
    # должен быть эндпоинт /api/secondhand/debug/error
    response = client.get("/api/secondhand/debug/error")
    assert response.status_code == 400
    data = response.json()
    assert data["error"] == "VALIDATION_ERROR"
    assert "Validation error:" in data["message"]


def test_upload_invalid_file_type_returns_validation_error(tmp_path):
    # используем debug-эндпоинт загрузки
    test_file = tmp_path / "test.txt"
    test_file.write_text("not an image")

    with test_file.open("rb") as f:
        response = client.post(
            "/api/ads/debug/upload-image",  # путь поправь под свой
            files={"image": ("test.txt", f, "text/plain")},
        )

    assert response.status_code == 400
    data = response.json()
    assert data["error"] == "VALIDATION_ERROR"
    assert "Only JPEG, PNG and WebP images are allowed" in data["message"]
