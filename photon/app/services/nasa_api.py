import requests


def fetch_cmr_collections(keyword: str = "MODIS", page_size: int = 20):
    """Fetch a small list of collections from NASA CMR (Earthdata). Returns simplified metadata list."""
    url = "https://cmr.earthdata.nasa.gov/search/collections.json"
    params = {"keyword": keyword, "page_size": page_size}
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    entries = r.json().get("feed", {}).get("entry", [])
    out = []
    for e in entries:
        out.append({
            "id": e.get("id"),
            "title": e.get("title"),
            "description": e.get("summary"),
            "links": e.get("links", []),
            "keywords": e.get("keywords", []),
        })
    return out
