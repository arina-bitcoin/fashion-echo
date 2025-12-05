from __future__ import annotations

import os
import time
from collections import defaultdict, deque
from typing import Deque, Dict, Tuple, Callable, Awaitable

from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.responses import PlainTextResponse


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


RATE_LIMIT = _env_int("RATE_LIMIT", 20)              # запросов
RATE_WINDOW_SECONDS = _env_int("RATE_WINDOW_SECONDS", 10)  # в этом окне
RATE_LIMIT_HEADER_NAME = "X-RateLimit-Limit"
RATE_REMAINING_HEADER_NAME = "X-RateLimit-Remaining"


class RateLimiterMiddleware:
    """
    Простой in-memory rate limiter (скользящее окно).
    Ключ: (ip, path). Поддерживает несколько воркеров в одном процессе.
    """

    def __init__(self, app: ASGIApp,
                 limit: int = RATE_LIMIT,
                 window_seconds: int = RATE_WINDOW_SECONDS) -> None:
        self.app = app
        self.limit = max(1, limit)
        self.window = max(1, window_seconds)
        self._hits: Dict[Tuple[str, str], Deque[float]] = defaultdict(deque)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        now = time.time()
        path = scope.get("path", "/")
        client = scope.get("client")
        ip = (client[0] if client else "unknown")
        key = (ip, path)

        q = self._hits[key]
        # удаляем «старые» события
        while q and now - q[0] >= self.window:
            q.popleft()

        # проверка лимита
        if len(q) >= self.limit:
            retry_after = max(1, int(self.window - (now - q[0])))
            resp = PlainTextResponse("Too Many Requests", status_code=429)
            resp.headers[RATE_LIMIT_HEADER_NAME] = str(self.limit)
            resp.headers[RATE_REMAINING_HEADER_NAME] = "0"
            resp.headers["Retry-After"] = str(retry_after)
            await resp(scope, receive, send)
            return

        # регистрируем запрос
        q.append(now)

        # оборачиваем отправку, чтобы дописать заголовки
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                remaining = max(0, self.limit - len(q))
                headers = message.setdefault("headers", [])
                headers.append((RATE_LIMIT_HEADER_NAME.encode(), str(self.limit).encode()))
                headers.append((RATE_REMAINING_HEADER_NAME.encode(), str(remaining).encode()))
            await send(message)

        await self.app(scope, receive, send_wrapper)
