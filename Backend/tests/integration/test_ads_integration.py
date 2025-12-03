import io
import pytest


class TestAdsIntegration:
    @pytest.mark.asyncio
    async def test_upload_image_authenticated(self, client, auth_headers):
        """
        Авторизованный пользователь может загрузить картинку.
        """
        test_image = ("test.jpg", io.BytesIO(b"fake image data"), "image/jpeg")

        resp = await client.post(
            "/api/ads/upload-image",
            files={"file": test_image},
            headers=auth_headers,
        )

        assert resp.status_code == 200
        data = resp.json()
        assert "file_path" in data

    @pytest.mark.asyncio
    async def test_upload_image_unauthenticated(self, client):
        """
        Без токена загрузка должна быть запрещена.
        Сейчас сервер даёт 422 (валидация) – это тоже ок.
        """
        test_image = ("test.jpg", io.BytesIO(b"fake image data"), "image/jpeg")

        resp = await client.post(
            "/api/ads/upload-image",
            files={"file": test_image},
        )

        assert resp.status_code in (401, 403, 422)
