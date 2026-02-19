import json
with open("data/vectors.json", encoding="utf-8") as f:
    data = json.load(f)
print(f"Total entries: {len(data)}")
for i, e in enumerate(data[:8]):
    meta = e.get("meta", {})
    title = meta.get("title", "?")[:55]
    url = meta.get("dataset_url") or meta.get("url") or "NO URL"
    fmt = meta.get("format", "?")
    var = meta.get("variable", "?")
    print(f"  [{i+1}] {title}")
    print(f"       URL: {str(url)[:80]}")
    print(f"       format={fmt}  variable={var}")
