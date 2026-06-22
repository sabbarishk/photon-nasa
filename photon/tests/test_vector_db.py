"""
Tests for vector_db.py — the ChromaDB-backed dataset index.

Strategy: use chromadb.EphemeralClient() (in-memory, no disk I/O) by setting
CHROMA_PERSIST_DIR=:memory: before each test. This means:
  - No Windows file-locking issues with temp directories
  - No leftover state between tests
  - Tests run in milliseconds (no disk writes)

get_embedding is mocked so that:
  - Tests don't load the sentence-transformers model
  - Embeddings are controlled, and the "right answer" is unambiguous
"""
from unittest.mock import patch

import app.services.vector_db as vdb


def _fresh():
    """Reset module singletons to a clean in-memory state."""
    vdb._reset(persist_dir=":memory:")
    return vdb


def _keyword_embedder(text: str, **_) -> list:
    """Return clearly-separated 3-D unit vectors based on topic keywords."""
    t = text.lower()
    if any(k in t for k in ("climate", "temperature", "giss", "warming")):
        return [1.0, 0.0, 0.0]
    if any(k in t for k in ("ocean", "salinity", "sea")):
        return [0.0, 1.0, 0.0]
    if any(k in t for k in ("mars", "geology", "crater")):
        return [0.0, 0.0, 1.0]
    return [0.33, 0.33, 0.33]


def test_add_and_search():
    """Adding three topically distinct datasets, searching by meaning returns the right one first."""
    db = _fresh()
    with patch("app.services.vector_db.get_embedding", side_effect=_keyword_embedder):
        db.add_dataset({
            "id": "giss-temp",
            "title": "GISS Global Temperature",
            "summary": "NASA GISS climate warming surface temperature anomalies",
            "format": "CSV",
            "tags": "climate,temperature",
            "source_url": "https://data.giss.nasa.gov/gistemp/",
        })
        db.add_dataset({
            "id": "ocean-sal",
            "title": "Ocean Salinity",
            "summary": "Global ocean salinity measurements from Argo floats",
            "format": "NetCDF",
            "tags": "ocean,salinity",
            "source_url": "https://example.com/salinity",
        })
        db.add_dataset({
            "id": "mars-geo",
            "title": "Mars Surface Geology",
            "summary": "Mars crater and geology mapping from MRO",
            "format": "HDF5",
            "tags": "mars,geology",
            "source_url": "https://example.com/mars",
        })

        # Semantic search for climate data — should rank giss-temp first
        results = db.search("global warming climate temperature trends", top_k=3)

    assert len(results) == 3
    assert results[0]["id"] == "giss-temp", (
        f"Expected 'giss-temp' first, got '{results[0]['id']}' "
        f"(scores: {[(r['id'], r['score']) for r in results]})"
    )
    # Score should be near 1.0 (cosine similarity of identical vectors)
    assert results[0]["score"] > 0.9
    # Response structure must match what the query route expects
    assert "meta" in results[0]
    assert results[0]["meta"]["format"] == "CSV"


def test_count():
    """count() returns the number of documents in the collection."""
    db = _fresh()

    def fixed_embed(text, **_):
        return [0.1, 0.2, 0.3]

    with patch("app.services.vector_db.get_embedding", side_effect=fixed_embed):
        assert db.count() == 0

        db.add_dataset({
            "id": "ds1", "title": "Alpha", "summary": "First dataset",
            "format": "CSV", "tags": "", "source_url": "",
        })
        assert db.count() == 1

        db.add_dataset({
            "id": "ds2", "title": "Beta", "summary": "Second dataset",
            "format": "JSON", "tags": "", "source_url": "",
        })
        assert db.count() == 2

        # Upsert is idempotent: re-adding an existing id must not increase count
        db.add_dataset({
            "id": "ds1", "title": "Alpha updated", "summary": "First dataset",
            "format": "CSV", "tags": "", "source_url": "",
        })
        assert db.count() == 2
