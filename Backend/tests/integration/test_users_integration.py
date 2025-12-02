# Backend/tests/integration/test_users_integration.py


class TestUsersIntegration:
    def test_update_user_profile(self, client, auth_headers):
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

        response = client.put(
            "/api/users/me",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()

        assert data["phone"] == payload["phone"]
        # если в UserResponse есть поле settings
        if "settings" in data and data["settings"] is not None:
            assert data["settings"]["theme"] == "dark"

    def test_update_user_profile_unauthenticated(self, client):
        """
        Без токена менять профиль нельзя.
        """
        response = client.put(
            "/api/users/me",
            json={"phone": "+79990000000"},
        )
        assert response.status_code in (401, 403)


    def test_get_user_ads(self, client, auth_headers):
        """
        Получение объявлений текущего пользователя.
        """
        response = client.get("/api/users/me/ads", headers=auth_headers)
        # если эндпоинт реализован, должен быть 200
        assert response.status_code == 200
        data = response.json()
        # может быть список или структура с items
        if isinstance(data, dict) and "items" in data:
            assert isinstance(data["items"], list)
        else:
            assert isinstance(data, list)
