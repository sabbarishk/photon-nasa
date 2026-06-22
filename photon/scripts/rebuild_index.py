"""Populate the ChromaDB index from the flat JSON source of truth.

Run once after install (or after adding new datasets to vectors.json):

    From repo root:
        python -m photon.scripts.rebuild_index

    From inside photon/:
        PYTHONPATH=. python scripts/rebuild_index.py

Upsert semantics mean it is safe to re-run: existing entries are updated,
not duplicated.
"""
import json
import os
import sys

# Ensure "photon/" is on sys.path so `from app.services...` imports resolve.
# __file__ = photon/scripts/rebuild_index.py  →  two levels up = photon/
_photon_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _photon_root not in sys.path:
    sys.path.insert(0, _photon_root)

from app.services.vector_db import add_dataset  # noqa: E402  (import after sys.path fix)


def main() -> None:
    vectors_path = os.path.join(_photon_root, "data", "vectors.json")
    if not os.path.exists(vectors_path):
        print(f"ERROR: {vectors_path} not found", file=sys.stderr)
        sys.exit(1)

    with open(vectors_path, "r", encoding="utf-8") as f:
        raw: list = json.load(f)

    for entry in raw:
        meta = entry.get("meta", {})
        add_dataset(
            {
                "id": entry["id"],
                "title": meta.get("title", ""),
                "summary": meta.get("summary", ""),
                "format": meta.get("format", ""),
                "tags": meta.get("keywords", ""),
                "source_url": meta.get("dataset_url", ""),
            }
        )
        print(f"  indexed: {entry['id']}")

    print(f"\nIndexed {len(raw)} datasets into ChromaDB.")


if __name__ == "__main__":
    main()
