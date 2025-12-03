import pytest


class TestSecondhandIntegration:
    @pytest.mark.asyncio
    async def test_get_secondhands_basic(self, client):
        """
        Список секондхендов без фильтров: /api/secondhand/
        """
        resp = await client.get("/api/secondhand/")

        assert resp.status_code == 200
        data = resp.json()

        assert "items" in data
        assert "total" in data
        assert isinstance(data["items"], list)

    @pytest.mark.asyncio
    async def test_get_secondhands_map_by_bounds(self, client):
        """
        Точки для карты по границам: /api/secondhand/map
        """
        resp = await client.get(
            "/api/secondhand/map",
            params={
                "ne_lat": 55.9,
                "ne_lng": 37.8,
                "sw_lat": 55.6,
                "sw_lng": 37.4,
            },
        )

        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_map_clusters(self, client):
        """
        Кластера для карты: /api/secondhand/map/clusters
        """
        resp = await client.get(
            "/api/secondhand/map/clusters",
            params={
                "zoom": 12,
                "ne_lat": 55.9,
                "ne_lng": 37.8,
                "sw_lat": 55.6,
                "sw_lng": 37.4,
            },
        )

        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

        if data:
            cluster = data[0]
            assert "count" in cluster
            assert "ids" in cluster
            assert ("lat" in cluster and "lng" in cluster) or (
                "latitude" in cluster and "longitude" in cluster
            )
