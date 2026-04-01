from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from starlette.testclient import TestClient

from app.csrf import CSRFMiddleware, CSRF_COOKIE, CSRF_FIELD


def _make_app():
    """Build a minimal FastAPI app with CSRF middleware for isolated testing."""
    test_app = FastAPI()
    test_app.add_middleware(CSRFMiddleware)

    @test_app.get("/form")
    async def get_form(request: Request):
        return PlainTextResponse(f"token={request.state.csrf_token}")

    @test_app.post("/submit")
    async def post_submit(request: Request):
        return PlainTextResponse("ok")

    return test_app


class TestCSRFMiddleware:
    def test_get_request_passes_without_csrf_token(self):
        app = _make_app()
        client = TestClient(app)
        resp = client.get("/form")
        assert resp.status_code == 200
        assert resp.text.startswith("token=")

    def test_get_sets_csrf_cookie(self):
        app = _make_app()
        client = TestClient(app)
        resp = client.get("/form")
        assert CSRF_COOKIE in resp.cookies

    def test_post_without_csrf_token_returns_403(self):
        app = _make_app()
        client = TestClient(app)
        resp = client.post("/submit", data={"field": "value"})
        assert resp.status_code == 403

    def test_post_with_valid_csrf_token_succeeds(self):
        app = _make_app()
        client = TestClient(app)

        # First GET to obtain a CSRF token
        get_resp = client.get("/form")
        token = get_resp.text.split("=", 1)[1]
        csrf_cookie = get_resp.cookies[CSRF_COOKIE]

        # POST with matching cookie + form field
        client.cookies.set(CSRF_COOKIE, csrf_cookie)
        post_resp = client.post("/submit", data={CSRF_FIELD: token})
        assert post_resp.status_code == 200
        assert post_resp.text == "ok"

    def test_post_with_wrong_token_returns_403(self):
        app = _make_app()
        client = TestClient(app)

        # GET to set a cookie
        get_resp = client.get("/form")
        csrf_cookie = get_resp.cookies[CSRF_COOKIE]

        # POST with a mismatched token
        client.cookies.set(CSRF_COOKIE, csrf_cookie)
        post_resp = client.post("/submit", data={CSRF_FIELD: "wrong-token"})
        assert post_resp.status_code == 403
