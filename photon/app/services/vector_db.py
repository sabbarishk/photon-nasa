import os

import chromadb

from app.services.hf_api import get_embedding

_CHROMA_DEFAULT = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data", "chroma")
)
_COLLECTION_NAME = "photon_datasets"
_PLAYBOOKS_COLLECTION_NAME = "photon_playbooks"

# Lazily initialized singletons — one client and one collection per process.
_client = None
_collection = None
_playbooks_collection = None


def _ensure_client() -> None:
    """Create the ChromaDB client if not yet initialized."""
    global _client
    if _client is not None:
        return
    persist_dir = os.environ.get("CHROMA_PERSIST_DIR", _CHROMA_DEFAULT)
    if persist_dir == ":memory:":
        _client = chromadb.EphemeralClient()
    else:
        persist_dir = os.path.normpath(persist_dir)
        os.makedirs(persist_dir, exist_ok=True)
        _client = chromadb.PersistentClient(path=persist_dir)


def _get_collection():
    global _collection
    if _collection is not None:
        return _collection
    _ensure_client()
    _collection = _client.get_or_create_collection(
        name=_COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )
    return _collection


def _get_playbooks_collection():
    global _playbooks_collection
    if _playbooks_collection is not None:
        return _playbooks_collection
    _ensure_client()
    _playbooks_collection = _client.get_or_create_collection(
        name=_PLAYBOOKS_COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )
    return _playbooks_collection


# ── Dataset store ────────────────────────────────────────────────────────────

def add_dataset(dataset: dict) -> None:
    """Embed and upsert one dataset into the ChromaDB collection.

    dataset keys: id, title, summary, format, tags, source_url
    All values must be strings (ChromaDB metadata restriction).
    """
    coll = _get_collection()
    doc_id = str(dataset["id"])
    title = str(dataset.get("title", ""))
    summary = str(dataset.get("summary", ""))
    text = f"{title}. {summary}"
    embedding = get_embedding(text)
    metadata = {
        "title": title,
        "summary": summary,
        "format": str(dataset.get("format", "")),
        "tags": str(dataset.get("tags", "")),
        "source_url": str(dataset.get("source_url", "")),
    }
    coll.upsert(
        ids=[doc_id],
        embeddings=[embedding],
        metadatas=[metadata],
        documents=[text],
    )


def search(query: str, top_k: int = 5) -> list:
    """Embed query and return top_k most similar datasets.

    Returns a list of dicts: {"id": str, "score": float, "meta": dict}
    Score is cosine similarity in [0, 1] (1 = identical).
    """
    coll = _get_collection()
    n = min(top_k, coll.count())
    if n == 0:
        return []
    emb = get_embedding(query)
    raw = coll.query(
        query_embeddings=[emb],
        n_results=n,
        include=["metadatas", "distances"],
    )
    ids = raw.get("ids", [[]])[0]
    metadatas = raw.get("metadatas", [[]])[0]
    distances = raw.get("distances", [[]])[0]
    return [
        {
            "id": ids[i],
            "score": round(1.0 - distances[i], 4),
            "meta": metadatas[i],
        }
        for i in range(len(ids))
    ]


def count() -> int:
    """Return the number of datasets currently indexed."""
    return _get_collection().count()


# ── Playbook store ───────────────────────────────────────────────────────────

def add_playbook(data_type: str, content: str) -> None:
    """Embed and upsert a methodology playbook document.

    data_type must match one of the profiler's output values:
    "tabular", "time_series", or "wide_format".
    """
    coll = _get_playbooks_collection()
    embedding = get_embedding(content)
    coll.upsert(
        ids=[f"playbook_{data_type}"],
        embeddings=[embedding],
        documents=[content],
        metadatas=[{"type": "playbook", "data_type": data_type}],
    )


def search_playbooks(data_type: str) -> str:
    """Return the methodology playbook for a given data type.

    This is a metadata filter query — not similarity search — because the
    profiler already gives us an exact classification. Returns empty string
    if no playbook has been loaded for this data type.
    """
    coll = _get_playbooks_collection()
    result = coll.get(
        where={"data_type": data_type},
        include=["documents"],
    )
    docs = result.get("documents", [])
    return docs[0] if docs else ""


# ── Test helpers ─────────────────────────────────────────────────────────────

def _reset(persist_dir: str = None) -> None:
    """Reset singleton state. For use in tests only.

    Deletes both collections before clearing references so that
    EphemeralClient (a process-level singleton in ChromaDB 1.x)
    starts clean for the next test.
    """
    global _client, _collection, _playbooks_collection
    if _client is not None:
        for name in (_COLLECTION_NAME, _PLAYBOOKS_COLLECTION_NAME):
            try:
                _client.delete_collection(name)
            except Exception:
                pass
    _client = None
    _collection = None
    _playbooks_collection = None
    if persist_dir is not None:
        os.environ["CHROMA_PERSIST_DIR"] = persist_dir
