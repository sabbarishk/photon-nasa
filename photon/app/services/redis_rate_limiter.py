import os
import time
from typing import Optional, Tuple

try:
    import redis.asyncio as aioredis
except Exception:
    aioredis = None


class RedisRateLimiter:
    """Redis-backed sliding-window rate limiter (fixed window)

    Usage:
      limiter = RedisRateLimiter(redis_url)
      allowed, retry_after = await limiter.allow(api_key)
    """

    def __init__(self, redis_url: Optional[str] = None, window: int = 60, limit: int = 120):
        if aioredis is None:
            raise RuntimeError('redis.asyncio package not installed')
        self.redis_url = redis_url or os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/0')
        self.window = int(os.getenv('RATE_WINDOW_SECONDS', window))
        self.limit = int(os.getenv('RATE_LIMIT_PER_WINDOW', limit))
        self._client = aioredis.from_url(self.redis_url, decode_responses=True)

    async def allow(self, api_key: str) -> Tuple[bool, Optional[int]]:
        """Return (allowed, retry_after_seconds).

        If allowed is False, retry_after is seconds until window resets.
        """
        now = int(time.time())
        window_index = now // self.window
        key = f"rl:{api_key}:{window_index}"

        # Use INCR and set EXPIRE only when key is new
        val = await self._client.incr(key)
        if val == 1:
            # Set TTL slightly longer than window
            await self._client.expire(key, self.window + 2)

        if val > self.limit:
            # calculate retry_after
            window_start = window_index * self.window
            retry_after = window_start + self.window - now
            if retry_after < 0:
                retry_after = 0
            return False, retry_after

        return True, None
