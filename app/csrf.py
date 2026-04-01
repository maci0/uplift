"""CSRF protection using the double-submit cookie pattern."""

import secrets

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from fastapi.responses import HTMLResponse

CSRF_COOKIE = "csrf_token"
CSRF_FIELD = "csrf_token"
_SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS", "TRACE"})


class CSRFMiddleware(BaseHTTPMiddleware):
    """Validate CSRF tokens on state-changing requests.

    On every request, a CSRF token is placed in request.state.csrf_token so
    templates can embed it as a hidden form field.  POST/PUT/DELETE requests
    must include a matching token in the form body.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        token = request.cookies.get(CSRF_COOKIE)
        new_token = False
        if not token:
            token = secrets.token_hex(32)
            new_token = True

        request.state.csrf_token = token

        if request.method not in _SAFE_METHODS:
            form = await request.form()
            # Cache form data on request.state so downstream routes can access it
            # (BaseHTTPMiddleware + call_next consumes the body stream)
            request.state.form_data = form
            form_token = form.get(CSRF_FIELD, "")
            if not form_token or not secrets.compare_digest(token, form_token):
                return HTMLResponse("CSRF validation failed", status_code=403)

        response = await call_next(request)

        if new_token:
            response.set_cookie(
                CSRF_COOKIE,
                token,
                httponly=True,
                samesite="strict",
                max_age=86400,
            )

        return response
