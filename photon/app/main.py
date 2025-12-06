from fastapi import FastAPI, Request
from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging

from app.routes import query, workflow, health
from app.services.auth import is_valid_key
import os
from app.services.redis_rate_limiter import RedisRateLimiter

app = FastAPI(title="Photon")

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger('photon')

app.include_router(query.router, prefix="/query", tags=["query"])
app.include_router(workflow.router, prefix="/workflow", tags=["workflow"])
app.include_router(health.router, prefix="", tags=["health"])


class ApiKeyRateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory API key auth + rate limiter.

    - Expects header `x-api-key`.
    - Skips auth for root, docs, and openapi endpoints.
    - Rate limit: 120 requests per 60-second window per API key (configurable constant below).
    """

    WINDOW_SECONDS = 60
    MAX_REQUESTS_PER_WINDOW = 120

    def __init__(self, app):
        super().__init__(app)
        # store: api_key -> {count, window_start}
        self._store = {}
        # optional Redis client for distributed rate limiting
        self._redis_limiter = None
        try:
            redis_url = os.getenv('REDIS_URL')
            if redis_url:
                self._redis_limiter = RedisRateLimiter(redis_url)
        except Exception:
            # fallback to in-memory limiter
            self._redis_limiter = None

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        # allow unauthenticated root and docs/openapi
        if path in ("/", "/openapi.json") or path.startswith("/docs") or path.startswith("/redoc"):
            return await call_next(request)
        # Optionally skip auth in dev with env var
        if os.getenv("PHOTON_SKIP_AUTH", "0") == "1":
            return await call_next(request)

        api_key = request.headers.get("x-api-key") or request.query_params.get("api_key")
        if not api_key or not is_valid_key(api_key):
            logger.warning("Unauthorized request to %s from %s", path, request.client)
            return JSONResponse({"detail": "Invalid or missing API key"}, status_code=401)

        # If Redis limiter available, use it for distributed rate limiting
        if self._redis_limiter is not None:
            try:
                allowed, retry = await self._redis_limiter.allow(api_key)
                if not allowed:
                    logger.warning("Rate limit exceeded for key %s on %s", api_key, path)
                    return JSONResponse({"detail": "Rate limit exceeded", "retry_after": retry}, status_code=429)
            except Exception:
                # if redis fails, fall back to in-memory limiter
                pass

        now = int(time.time())
        rec = self._store.get(api_key)
        if rec is None or now >= rec["window_start"] + self.WINDOW_SECONDS:
            # reset window
            self._store[api_key] = {"count": 1, "window_start": now}
        else:
            rec["count"] += 1
            if rec["count"] > self.MAX_REQUESTS_PER_WINDOW:
                retry_after = rec["window_start"] + self.WINDOW_SECONDS - now
                logger.warning("Rate limit exceeded for key %s on %s", api_key, path)
                return JSONResponse({"detail": "Rate limit exceeded", "retry_after": retry_after}, status_code=429)

        return await call_next(request)


app.add_middleware(ApiKeyRateLimitMiddleware)


@app.get("/")
def root():
    return {"status": "photon backend OK"}
