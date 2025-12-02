import pytest


class TestUsersIntegration:
    @pytest.mark.asyncio
    async def test_update_user_profile(self, client, auth_headers):
        """
        Обновление профиля пользователя + настроек.
        """
        payload = {
            "phone": "+79991234567",
            "settings": {
                "theme": "dark",
                "notifications": True,
            },
        }

        response = await client.put(
            "/api/users/me",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        assert data["phone"] == payload["phone"]
        if "settings" in data and data["settings"] is not None:
            assert data["settings"]["theme"] == "dark"

    @pytest.mark.asyncio
    async def test_update_user_profile_unauthenticated(self, client):
        """
        Без токена менять профиль нельзя.
        """
        response = await client.put(
            "/api/users/me",
            json={"phone": "+79990000000"},
        )
        assert response.status_code in (401, 403)

    @pytest.mark.asyncio
    async def test_get_user_ads(self, client, auth_headers):
        """
        Получение объявлений текущего пользователя.
        """
        response = await client.get("/api/users/me/ads", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        if isinstance(data, dict) and "items" in data:
            assert isinstance(data["items"], list)
        else:
            assert isinstance(data, list)
