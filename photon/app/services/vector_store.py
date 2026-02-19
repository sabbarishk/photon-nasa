import os
import json
import math
import numpy as np

_chroma_available = False
try:
    import chromadb
    from chromadb.config import Settings
    _chroma_available = True
except Exception:
    chromadb = None
    Settings = None


class VectorStore:
    """Vector store with pluggable backends.

    Supported backends:
    - 'file' (default): simple JSON file stored at `path`.
    - future backends: weaviate/chroma (placeholder hooks)
    """

    def __init__(self, path: str = "data/vectors.json", backend: str = None, **kwargs):
        self.backend = backend or os.getenv('VECTOR_STORE_BACKEND', 'file')
        self.path = os.path.normpath(path)
        self._chroma_client = None
        self._chroma_collection = None
        # In-memory cache for file backend: loaded once, kept hot
        self._cache = None
        if self.backend == 'file':
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            if not os.path.exists(self.path):
                with open(self.path, 'w', encoding='utf-8') as f:
                    json.dump([], f)
            # Pre-load into memory at startup
            self._cache = self._load_from_disk()
        else:
            # Placeholder for managed backends. Try to lazy-load client when used.
            if self.backend == 'chroma' and not _chroma_available:
                raise RuntimeError('chroma backend requested but chromadb package not installed')

    def _init_chroma(self, persist_directory: str = None, collection_name: str = 'photon'):
        if not _chroma_available:
            raise RuntimeError('chromadb not installed')
        if self._chroma_collection is not None:
            return
        # Determine persist directory: parameter -> env var -> default
        pd = persist_directory or os.getenv('CHROMA_PERSIST_DIR') or os.path.normpath(os.path.join(os.path.dirname(self.path), '..', 'data', 'chroma'))
        # If the caller explicitly requested in-memory (e.g. ':memory:'), use the simple Client()
        if isinstance(pd, str) and pd.strip() == ':memory:':
            client = chromadb.Client()
        else:
            pd = os.path.normpath(pd)
            os.makedirs(pd, exist_ok=True)
            try:
                settings = Settings(chroma_db_impl="duckdb+parquet", persist_directory=pd)
                try:
                    client = chromadb.PersistentClient(settings)
                except Exception:
                    client = chromadb.Client()
            except Exception:
                client = chromadb.Client()

        try:
            col = client.get_collection(collection_name)
        except Exception:
            col = client.create_collection(name=collection_name)
        self._chroma_client = client
        self._chroma_collection = col

    def _load_from_disk(self):
        """Read from JSON file. Used at init and after writes."""
        try:
            if os.path.getsize(self.path) == 0:
                return []
        except Exception:
            pass
        with open(self.path, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []

    def _load(self):
        if self.backend == 'file':
            # Return in-memory cache; fall back to disk if cache not set
            if self._cache is not None:
                return self._cache
            return self._load_from_disk()
        else:
            raise NotImplementedError(f"Backend '{self.backend}' not implemented in this build")

    def _save(self, objects):
        if self.backend == 'file':
            with open(self.path, 'w', encoding='utf-8') as f:
                json.dump(objects, f, ensure_ascii=False, indent=2)
            # Update cache
            self._cache = objects
        else:
            raise NotImplementedError(f"Backend '{self.backend}' not implemented in this build")

    def add(self, id: str, meta: dict, embedding: list):
        if self.backend == 'file':
            objs = self._load()
            objs.append({"id": id, "meta": meta, "embedding": embedding})
            self._save(objs)
        elif self.backend == 'chroma':
            # lazy init
            self._init_chroma()
            self._chroma_collection.add(ids=[id], embeddings=[embedding], metadatas=[meta], documents=[meta.get('text', '')])
        else:
            raise NotImplementedError(f"Backend '{self.backend}' not implemented in this build")

    def _cosine(self, a, b):
        a = np.array(a, dtype=float)
        b = np.array(b, dtype=float)
        if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
            return 0.0
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

    def search(self, embedding: list, top_k: int = 5):
        if self.backend == 'file':
            objs = self._load()
            if not objs:
                return []

            # Vectorized cosine similarity for fast batch scoring
            query_vec = np.array(embedding, dtype=float)
            query_norm = np.linalg.norm(query_vec)

            valid_objs = [o for o in objs if o.get("embedding")]
            if not valid_objs:
                return []

            # Stack all embeddings into a matrix for bulk computation
            matrix = np.array([o["embedding"] for o in valid_objs], dtype=float)
            norms = np.linalg.norm(matrix, axis=1)

            # Avoid division by zero
            with np.errstate(divide='ignore', invalid='ignore'):
                scores = np.where(
                    (norms > 0) & (query_norm > 0),
                    matrix.dot(query_vec) / (norms * query_norm),
                    0.0
                )

            # Get top_k indices
            top_indices = np.argpartition(scores, -min(top_k, len(scores)))[-min(top_k, len(scores)):]
            top_indices = top_indices[np.argsort(scores[top_indices])[::-1]]

            results = []
            for idx in top_indices:
                o = valid_objs[idx]
                results.append({"id": o.get("id"), "score": float(scores[idx]), "meta": o.get("meta")})
            return results
        elif self.backend == 'chroma':
            self._init_chroma()
            # The chroma client expects include to contain valid items; 'ids' is not a valid include
            # value for some chroma versions, so request metadatas and distances and read ids
            resp = self._chroma_collection.query(query_embeddings=[embedding], n_results=top_k, include=["metadatas", "distances"])
            results = []
            # chroma returns lists per query; take first
            ids = resp.get('ids', [[]])[0]
            metadatas = resp.get('metadatas', [[]])[0]
            distances = resp.get('distances', [[]])[0]
            for i in range(len(ids)):
                results.append({"id": ids[i], "score": None if distances is None else distances[i], "meta": metadatas[i]})
            return results
        else:
            raise NotImplementedError(f"Backend '{self.backend}' not implemented in this build")
