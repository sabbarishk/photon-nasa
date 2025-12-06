Redis Rate Limiter

This project supports a Redis-backed rate limiter for production/multi-instance usage.

How it works
- Set `REDIS_URL` in the environment (e.g., `redis://127.0.0.1:6379/0`). The middleware will use Redis to count requests per fixed time window.
- If `REDIS_URL` is not set or Redis is unreachable, the server falls back to the in-memory per-process limiter.

Local dev with Docker Compose
1. From repo root, start Redis:

```powershell
docker compose -f docker\docker-compose.redis.yml up -d
```

2. Start the server with Redis enabled:

```powershell
$env:PYTHONPATH = Join-Path (Get-Location).Path 'photon'
$env:REDIS_URL = 'redis://127.0.0.1:6379/0'
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Notes
- The Redis limiter uses a fixed window counter (INCR + EXPIRE). For tighter rate control use sliding window or leaky bucket algorithms.
- For distributed deployments, ensure Redis is secured and monitored.
