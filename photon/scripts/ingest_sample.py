r"""Ingest sample NASA CMR collections into the file-based vector store.

Run from project root with your HF_TOKEN set and venv activated:
    python .\scripts\ingest_sample.py --keyword MODIS --limit 10

This script fetches collections, creates a short text for each, asks HF for an embedding,
and saves entries to data/vectors.json using the VectorStore.
"""
import argparse
import time
from app.services.nasa_api import fetch_cmr_collections
from app.services.hf_api import get_embedding
from app.services.vector_store import VectorStore


def make_text(item: dict) -> str:
    parts = [item.get("title", ""), item.get("description", "")]
    kws = item.get("keywords") or []
    if kws:
        parts.append("keywords: " + ", ".join(kws[:10]))
    return " \n ".join([p for p in parts if p])


def ingest(keyword: str = "MODIS", limit: int = 10):
    print(f"Fetching up to {limit} collections for keyword '{keyword}'...")
    items = fetch_cmr_collections(keyword=keyword, page_size=limit)
    print(f"Fetched {len(items)} items. Computing embeddings and saving...")

    vs = VectorStore("data/vectors.json")
    added = 0
    for idx, it in enumerate(items[:limit]):
        doc_id = it.get("id") or f"item-{idx}"
        text = make_text(it)
        try:
            emb = get_embedding(text)
        except Exception as e:
            print(f"Embedding failed for {doc_id}: {e}")
            print("Skipping this item and continuing with next.")
            continue
        meta = {"title": it.get("title"), "description": it.get("description"), "keywords": it.get("keywords")}
        vs.add(doc_id, meta, emb)
        added += 1
        print(f"[{added}] Added {doc_id}")
        time.sleep(0.5)

    print(f"Ingest complete. {added} items added to {vs.path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--keyword", default="MODIS")
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()
    ingest(keyword=args.keyword, limit=args.limit)
