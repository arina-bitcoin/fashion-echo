# Backend/tests/integration/test_files_integration.py

import io


class TestFilesIntegration:
    def test_upload_ad_image(self, client, auth_headers):
        """
        Успешная загрузка корректного изображения.
        """
        test_image = ("test.jpg", io.BytesIO(b"fake image data"), "image/jpeg")

        resp = client.post(
            "/api/ads/upload-image",
            files={"file": test_image},
            headers=auth_headers,
        )

        assert resp.status_code == 200
        data = resp.json()
        assert "file_path" in data

    def test_upload_ad_image_wrong_content_type(self, client, auth_headers):
        """
        Невалидный тип файла → ValidationException → 400.
        """
        bad_file = ("test.txt", io.BytesIO(b"not image"), "text/plain")

        resp = client.post(
            "/api/ads/upload-image",
            files={"file": bad_file},
            headers=auth_headers,
        )

        assert resp.status_code == 400
        data = resp.json()
        assert data["error"] == "VALIDATION_ERROR"
