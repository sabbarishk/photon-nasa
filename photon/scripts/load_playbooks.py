"""Ingest methodology playbooks from photon/data/playbooks/ into ChromaDB.

Run from the repo root:
    python -m photon.scripts.load_playbooks
"""
import os
import sys

_photon_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _photon_root not in sys.path:
    sys.path.insert(0, _photon_root)

from app.services.vector_db import add_playbook

_PLAYBOOKS_DIR = os.path.join(_photon_root, "data", "playbooks")
_DATA_TYPES = ["tabular", "time_series", "wide_format"]


def main() -> None:
    loaded = 0
    for data_type in _DATA_TYPES:
        path = os.path.join(_PLAYBOOKS_DIR, f"{data_type}.md")
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        add_playbook(data_type, content)
        print(f"  loaded: {data_type}")
        loaded += 1
    print(f"\nLoaded {loaded} playbooks into ChromaDB.")


if __name__ == "__main__":
    main()
