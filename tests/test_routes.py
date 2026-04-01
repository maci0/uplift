from app.models import Product, Score, Tag


def _csrf(client):
    """Get a CSRF token by hitting any page."""
    client.get("/about")
    return client.cookies.get("csrf_token", "test")


def _post(client, url, data=None, **kwargs):
    """POST with CSRF token included."""
    token = _csrf(client)
    if data is None:
        data = {}
    if isinstance(data, dict):
        data["csrf_token"] = token
    elif isinstance(data, list):
        data.append(("csrf_token", token))
    return client.post(url, data=data, **kwargs)


class TestDashboard:
    def test_get_root_returns_200(self, client):
        resp = client.get("/")
        assert resp.status_code == 200

    def test_org_history_returns_200(self, client):
        resp = client.get("/org-history")
        assert resp.status_code == 200


class TestHealth:
    def test_get_health_returns_healthy(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert data["database"] == "connected"
        assert data["db_response_ms"] >= 0


class TestPages:
    def test_docs_returns_200(self, client):
        resp = client.get("/docs")
        assert resp.status_code == 200

    def test_about_returns_200(self, client):
        resp = client.get("/about")
        assert resp.status_code == 200

    def test_github_redirects(self, client):
        resp = client.get("/github", follow_redirects=False)
        assert resp.status_code == 303
        assert "github.com" in resp.headers["location"]


class TestProductIndex:
    def test_get_products_returns_200(self, client):
        resp = client.get("/products/")
        assert resp.status_code == 200

    def test_assessed_filter(self, client, db):
        p1 = Product(name="Assessed", product_type="Product", is_active=True, is_assessed=True)
        p2 = Product(name="Not Assessed", product_type="Product", is_active=True, is_assessed=False)
        db.add_all([p1, p2])
        db.commit()
        resp = client.get("/products/?assessed=1")
        assert resp.status_code == 200
        assert b"Assessed" in resp.content
        assert b"Not Assessed" not in resp.content


class TestProductShow:
    def test_get_product_returns_200(self, client, sample_product):
        resp = client.get(f"/products/{sample_product.id}")
        assert resp.status_code == 200

    def test_nonexistent_product_redirects(self, client):
        resp = client.get("/products/99999", follow_redirects=False)
        assert resp.status_code == 303

    def test_inactive_product_redirects(self, client, sample_product, db):
        sample_product.is_active = False
        db.commit()
        resp = client.get(f"/products/{sample_product.id}", follow_redirects=False)
        assert resp.status_code == 303


class TestProductCreate:
    def test_get_new_form(self, client):
        resp = client.get("/products/new")
        assert resp.status_code == 200

    def test_create_product(self, client, db):
        resp = _post(client, "/products/", data={
            "name": "New Product", "product_type": "Product"
        }, follow_redirects=False)
        assert resp.status_code == 303
        assert "msg=asset_created" in resp.headers["location"]

    def test_create_empty_name_redirects(self, client):
        resp = _post(client, "/products/", data={
            "name": "", "product_type": "Product"
        }, follow_redirects=False)
        assert resp.status_code == 303
        assert "new" in resp.headers["location"]

    def test_create_name_over_255_redirects(self, client):
        resp = _post(client, "/products/", data={
            "name": "x" * 256, "product_type": "Product"
        }, follow_redirects=False)
        assert resp.status_code == 303

    def test_create_invalid_type_redirects(self, client):
        resp = _post(client, "/products/", data={
            "name": "Test", "product_type": "InvalidType"
        }, follow_redirects=False)
        assert resp.status_code == 303
        assert "new" in resp.headers["location"]

    def test_create_with_tags(self, client, db):
        token = _csrf(client)
        resp = client.post("/products/", data={
            "name": "Tagged", "product_type": "Service",
            "tag_key": ["team", "env"], "tag_value": ["Platform", "prod"],
            "csrf_token": token,
        }, follow_redirects=False)
        assert resp.status_code == 303
        product = db.query(Product).filter(Product.name == "Tagged").first()
        assert product is not None
        assert len(product.tags) == 2


class TestProductUpdate:
    def test_get_edit_form(self, client, sample_product):
        resp = client.get(f"/products/{sample_product.id}/edit")
        assert resp.status_code == 200

    def test_update_product(self, client, sample_product, db):
        resp = _post(client, f"/products/{sample_product.id}", data={
            "name": "Updated", "product_type": "Service"
        }, follow_redirects=False)
        assert resp.status_code == 303
        assert "msg=asset_updated" in resp.headers["location"]
        db.refresh(sample_product)
        assert sample_product.name == "Updated"

    def test_update_nonexistent_redirects(self, client):
        resp = _post(client, "/products/99999", data={
            "name": "Test", "product_type": "Product"
        }, follow_redirects=False)
        assert resp.status_code == 303

    def test_update_invalid_type_redirects(self, client, sample_product):
        resp = _post(client, f"/products/{sample_product.id}", data={
            "name": "Test", "product_type": "BadType"
        }, follow_redirects=False)
        assert resp.status_code == 303
        assert "edit" in resp.headers["location"]


class TestProductDelete:
    def test_delete_marks_inactive(self, client, sample_product, db):
        resp = _post(client, f"/products/{sample_product.id}/delete", follow_redirects=False)
        assert resp.status_code == 303
        assert "msg=asset_deleted" in resp.headers["location"]
        db.refresh(sample_product)
        assert sample_product.is_active is False

    def test_delete_nonexistent_redirects(self, client):
        resp = _post(client, "/products/99999/delete", follow_redirects=False)
        assert resp.status_code == 303


class TestScores:
    def test_scores_index(self, client, sample_product):
        resp = client.get(f"/products/{sample_product.id}/scores/")
        assert resp.status_code == 200

    def test_scores_index_nonexistent_product(self, client):
        resp = client.get("/products/99999/scores/", follow_redirects=False)
        assert resp.status_code == 303

    def test_score_show(self, client, sample_product, sample_score):
        resp = client.get(f"/products/{sample_product.id}/scores/{sample_score.id}")
        assert resp.status_code == 200

    def test_score_show_nonexistent(self, client, sample_product):
        resp = client.get(f"/products/{sample_product.id}/scores/99999", follow_redirects=False)
        assert resp.status_code == 303

    def test_new_score_form(self, client, sample_product):
        resp = client.get(f"/products/{sample_product.id}/scores/new")
        assert resp.status_code == 200

    def test_create_score(self, client, sample_product):
        data = {}
        for prefix, count in [("a", 12), ("b", 8), ("c", 10), ("d", 8), ("e", 4)]:
            for i in range(1, count + 1):
                data[f"{prefix}{i}"] = "3"
        resp = _post(client, f"/products/{sample_product.id}/scores/", data=data, follow_redirects=False)
        assert resp.status_code == 303
        assert "msg=score_saved" in resp.headers["location"]

    def test_create_score_archives_previous(self, client, sample_product, sample_score, db):
        assert sample_score.latest is True
        data = {f"a{i}": "2" for i in range(1, 13)}
        resp_post = _post(client, f"/products/{sample_product.id}/scores/", data=data)
        db.refresh(sample_score)
        assert sample_score.latest is False

    def test_create_score_invalid_values_ignored(self, client, sample_product, db):
        data = {"a1": "5", "a2": "0", "a3": "abc", "a4": "2"}
        resp_post = _post(client, f"/products/{sample_product.id}/scores/", data=data)
        score = db.query(Score).filter(Score.product_id == sample_product.id, Score.latest.is_(True)).first()
        assert score is not None
        assert score.a1 is None  # 5 is out of range
        assert score.a2 is None  # 0 is out of range
        assert score.a3 is None  # non-digit
        assert score.a4 == 2     # valid

    def test_create_score_non_assessable_redirects(self, client, db):
        product = Product(name="Locked", product_type="Product", is_active=True, is_assessable=False)
        db.add(product)
        db.commit()
        db.refresh(product)
        resp = _post(client, f"/products/{product.id}/scores/", data={"a1": "2"}, follow_redirects=False)
        assert resp.status_code == 303


class TestTags:
    def test_new_tag_form(self, client, sample_product):
        resp = client.get(f"/products/{sample_product.id}/tags/new")
        assert resp.status_code == 200

    def test_create_tag(self, client, sample_product):
        resp = _post(client, f"/products/{sample_product.id}/tags/",
            data={"key": "env", "value": "prod"}, follow_redirects=False)
        assert resp.status_code == 303
        assert "msg=tag_added" in resp.headers["location"]

    def test_create_empty_key_redirects(self, client, sample_product):
        resp = _post(client, f"/products/{sample_product.id}/tags/",
            data={"key": "  ", "value": "val"}, follow_redirects=False)
        assert resp.status_code == 303
        assert "new" in resp.headers["location"]

    def test_create_duplicate_key(self, client, sample_product, db):
        db.add(Tag(key="env", value="prod", product_id=sample_product.id))
        db.commit()
        resp = _post(client, f"/products/{sample_product.id}/tags/",
            data={"key": "env", "value": "staging"}, follow_redirects=False)
        assert resp.status_code == 303
        assert "msg=tag_duplicate" in resp.headers["location"]

    def test_edit_tag_form(self, client, sample_product, db):
        tag = Tag(key="env", value="prod", product_id=sample_product.id)
        db.add(tag)
        db.commit()
        db.refresh(tag)
        resp = client.get(f"/products/{sample_product.id}/tags/{tag.id}/edit")
        assert resp.status_code == 200

    def test_update_tag(self, client, sample_product, db):
        tag = Tag(key="env", value="prod", product_id=sample_product.id)
        db.add(tag)
        db.commit()
        db.refresh(tag)
        resp = _post(client, f"/products/{sample_product.id}/tags/{tag.id}",
            data={"key": "env", "value": "staging"}, follow_redirects=False)
        assert resp.status_code == 303
        assert "msg=tag_updated" in resp.headers["location"]

    def test_update_nonexistent_tag(self, client, sample_product):
        resp = _post(client, f"/products/{sample_product.id}/tags/99999",
            data={"key": "env", "value": "prod"}, follow_redirects=False)
        assert resp.status_code == 303

    def test_delete_tag(self, client, sample_product, db):
        tag = Tag(key="env", value="prod", product_id=sample_product.id)
        db.add(tag)
        db.commit()
        db.refresh(tag)
        resp = _post(client, f"/products/{sample_product.id}/tags/{tag.id}/delete",
            follow_redirects=False)
        assert resp.status_code == 303
        assert "msg=tag_deleted" in resp.headers["location"]

    def test_delete_nonexistent_tag(self, client, sample_product):
        resp = _post(client, f"/products/{sample_product.id}/tags/99999/delete",
            follow_redirects=False)
        assert resp.status_code == 303


class TestDump:
    def test_get_dump_returns_json_array(self, client):
        resp = client.get("/dump")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_dump_includes_assessed_product(self, client, sample_product, sample_score):
        resp = client.get("/dump")
        data = resp.json()
        names = [item["productInfo"]["name"] for item in data]
        assert "Test Product" in names

    def test_dump_data_structure(self, client, sample_product, sample_score):
        resp = client.get("/dump")
        item = resp.json()[0]
        assert "productInfo" in item
        assert "categories" in item
        assert "capabilities" in item
        assert "cloudScore" in item

    def test_dump_excludes_inactive(self, client, sample_product, sample_score, db):
        sample_product.is_active = False
        db.commit()
        resp = client.get("/dump")
        names = [item["productInfo"]["name"] for item in resp.json()]
        assert "Test Product" not in names
