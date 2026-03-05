from __future__ import annotations

import os
from typing import Iterable, Tuple

from starlette.types import ASGIApp, Receive, Scope, Send

CSP = os.getenv(
    "CSP",
    "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; img-src 'self' data: https://fastapi.tiangolo.com; object-src 'none'; frame-ancestors 'none'; base-uri 'self'"
)
USE_HSTS = os.getenv("USE_HSTS", "0") in ("1", "true", "True")


class SecurityHeadersMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers: list[Tuple[bytes, bytes]] = message.setdefault("headers", [])

                def add(name: str, value: str):
                    headers.append((name.encode(), value.encode()))

                add("X-Content-Type-Options", "nosniff")
                add("X-Frame-Options", "DENY")
                add("Referrer-Policy", "no-referrer")
                add("Permissions-Policy", "geolocation=(), microphone=(), camera=()")
                add("Content-Security-Policy", CSP)
                if USE_HSTS:
                    add("Strict-Transport-Security", "max-age=63072000; includeSubDomains; preload")

            await send(message)

        await self.app(scope, receive, send_wrapper)
