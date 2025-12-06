"""Quick smoke test for local Chromadb persistence.
Creates a small collection under `photon/data/chroma_test`, inserts two vectors, and queries them.
Run with: python .\photon\scripts\test_chroma_local.py (from repo root) or use PYTHONPATH if needed.
"""
import os
import json

def run():
    try:
        import chromadb
        from chromadb.config import Settings
    except Exception as e:
        print("chromadb is not installed or failed to import:\n", e)
        print("Install with: python -m pip install chromadb")
        return

    persist_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'chroma_test'))
    os.makedirs(persist_dir, exist_ok=True)

    # Try persistent client first (may require native bindings); fall back to in-memory client.
    client = None
    try:
        settings = Settings(chroma_db_impl="duckdb+parquet", persist_directory=persist_dir)
        try:
            client = chromadb.PersistentClient(settings)
            print("Using PersistentClient (duckdb+parquet)")
        except Exception as e:
            print("PersistentClient failed, falling back to in-memory Client. Error:", e)
            client = chromadb.Client()

        coll = client.get_or_create_collection("photon_test_collection")

        # small vectors (3-d) for smoke test
        ids = ["v1", "v2"]
        metadatas = [{"text": "hello world"}, {"text": "goodbye"}]
        embeddings = [[0.1, 0.2, 0.3], [0.1, 0.2, 0.25]]

        # clear existing entries with same ids if present
        try:
            coll.delete(ids=ids)
        except Exception:
            pass

        coll.add(ids=ids, metadatas=metadatas, embeddings=embeddings)

        query = [[0.1, 0.2, 0.3]]
        results = coll.query(query_embeddings=query, n_results=2)
        print("Query results:\n", json.dumps(results, indent=2))

        # persist if available
        try:
            if hasattr(client, 'persist'):
                client.persist()
        except Exception:
            pass

        print("Chroma smoke test completed — persist dir:", persist_dir)
    except Exception as e:
        print("Chroma client error:", e)

if __name__ == '__main__':
    run()
