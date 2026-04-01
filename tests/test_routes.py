class TestDashboard:
    def test_get_root_returns_200(self, client):
        resp = client.get("/")
        assert resp.status_code == 200


class TestHealth:
    def test_get_health_returns_healthy(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestProducts:
    def test_get_products_returns_200(self, client):
        resp = client.get("/products/")
        assert resp.status_code == 200


class TestDump:
    def test_get_dump_returns_json_array(self, client):
        resp = client.get("/dump")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    def test_dump_includes_assessed_product(self, client, sample_product, sample_score):
        """A product that is active, assessed, and has a latest score should appear in dump."""
        resp = client.get("/dump")
        assert resp.status_code == 200
        data = resp.json()
        names = [item["productInfo"]["name"] for item in data]
        assert "Test Product" in names
