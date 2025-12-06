# API Keys & Rate Limiting (Backend)

This project includes a simple API-key based auth and an in-memory rate limiter for pilot/testing.

How it works
- Middleware checks `x-api-key` header or `api_key` query parameter for all endpoints except `/`, `/docs`, and OpenAPI.
- Rate limit: 120 requests per 60 seconds per API key (changeable in `app/main.py`).

Create an API key
1. Activate your venv and set PYTHONPATH so the package imports work in scripts (from repo root):

```powershell
$env:PYTHONPATH = (Get-Location).Path
.\photon\venv\Scripts\Activate.ps1
python .\photon\scripts\create_api_key.py
```

This prints the new key and persists it to `data/api_keys.json`.

Development convenience
- To run the server without API key checks (dev only), set the environment variable `PHOTON_SKIP_AUTH=1` before starting the server.

Notes
- The current rate limiter is per-process memory only. For multi-instance production, use Redis or a managed rate-limiter.
- For production, replace the file-based key store with a secure DB and rotate keys regularly.
