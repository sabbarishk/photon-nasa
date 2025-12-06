import os
import tempfile
import json

from app.services.vector_store import VectorStore


def test_file_backend_add_and_search():
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
    tmp.close()
    try:
        vs = VectorStore(path=tmp.name, backend='file')
        vs.add('id1', {'text': 'hello'}, [0.0, 1.0, 0.0])
        vs.add('id2', {'text': 'world'}, [1.0, 0.0, 0.0])
        res = vs.search([1.0, 0.0, 0.0], top_k=2)
        assert isinstance(res, list)
        assert res[0]['id'] == 'id2'
    finally:
        try:
            os.unlink(tmp.name)
        except Exception:
            pass


def test_chroma_backend_smoke():
    # only run if chromadb installed
    try:
        vs = VectorStore(path=':memory:', backend='chroma')
    except Exception:
        return
    vs.add('c1', {'text': 'a'}, [0.1, 0.2, 0.3])
    res = vs.search([0.1, 0.2, 0.3], top_k=1)
    assert isinstance(res, list)
