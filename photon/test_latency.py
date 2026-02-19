"""Quick latency check with session keep-alive."""
import time
import requests

s = requests.Session()

# warmup
s.post("http://localhost:8000/query/", json={"query": "warmup", "top_k": 1}, timeout=30)

for q in ["sea surface temperature", "MODIS vegetation index", "Arctic ice thickness"]:
    t0 = time.time()
    r = s.post("http://localhost:8000/query/", json={"query": q, "top_k": 3}, timeout=30)
    elapsed = (time.time() - t0) * 1000
    title = r.json()["results"][0]["meta"].get("title", "?")[:50]
    print(f"{elapsed:.0f}ms  {r.status_code}  {title}")
