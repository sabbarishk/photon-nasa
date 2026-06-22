import os

import chromadb

from app.services.hf_api import get_embedding

_CHROMA_DEFAULT = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data", "chroma")
)
_COLLECTION_NAME = "photon_datasets"

# Lazily initialized singletons — one client and one collection per process.
_client = None
_collection = None


def _get_collection():
    global _client, _collection
    if _collection is not None:
        return _collection
    persist_dir = os.path.normpath(
        os.environ.get("CHROMA_PERSIST_DIR", _CHROMA_DEFAULT)
    )
    os.makedirs(persist_dir, exist_ok=True)
    _client = chromadb.PersistentClient(path=persist_dir)
    _collection = _client.get_or_create_collection(
        name=_COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )
    return _collection


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


def _reset(persist_dir: str = None) -> None:
    """Reset singleton state. For use in tests only."""
    global _client, _collection
    _client = None
    _collection = None
    if persist_dir is not None:
        os.environ["CHROMA_PERSIST_DIR"] = persist_dir
