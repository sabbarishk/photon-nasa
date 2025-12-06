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
        if self.backend == 'file':
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            if not os.path.exists(self.path):
                with open(self.path, 'w', encoding='utf-8') as f:
                    json.dump([], f)
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
            # Prefer an in-process persistent client when a filesystem path is provided.
            # Some chromadb versions raise on legacy config values; fall back to the simple Client()
            try:
                settings = Settings(chroma_db_impl="duckdb+parquet", persist_directory=pd)
                # Attempt to construct a persistent client; if it fails, fall back to simple Client()
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

    def _load(self):
        if self.backend == 'file':
            # tolerate empty files
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
        else:
            raise NotImplementedError(f"Backend '{self.backend}' not implemented in this build")

    def _save(self, objects):
        if self.backend == 'file':
            with open(self.path, 'w', encoding='utf-8') as f:
                json.dump(objects, f, ensure_ascii=False, indent=2)
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
            scores = []
            for o in objs:
                emb = o.get("embedding")
                if not emb:
                    continue
                score = self._cosine(embedding, emb)
                scores.append((score, o))
            scores.sort(key=lambda x: x[0], reverse=True)
            results = []
            for score, o in scores[:top_k]:
                results.append({"id": o.get("id"), "score": score, "meta": o.get("meta")})
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
