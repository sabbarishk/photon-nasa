"""Quick speed test for search pipeline."""
import time
import sys
sys.path.insert(0, '.')

from app.services.hf_api import get_embedding
from app.services.vector_store import VectorStore

print('Loading vector store...')
start = time.time()
vs = VectorStore('data/vectors.json')
load_time = time.time() - start
print(f'Vector store loaded in {load_time:.2f}s, entries: {len(vs._cache) if vs._cache else 0}')
print()

print('Warming up embedding model (first load)...')
start = time.time()
_ = get_embedding('warmup')
warmup_time = time.time() - start
print(f'Model loaded in {warmup_time:.2f}s')
print()

queries = ['sea surface temperature', 'MODIS land surface reflectance', 'ice sheet glacier elevation']
for q in queries:
    start = time.time()
    emb = get_embedding(q)
    results = vs.search(emb, top_k=5)
    elapsed = time.time() - start
    title = results[0]['meta'].get('title', '?')[:60] if results else 'no results'
    score = results[0]['score'] if results else 0
    print(f'Search "{q}"')
    print(f'  Time: {elapsed*1000:.0f}ms | Results: {len(results)} | Top: {title} ({score:.3f})')
print()
print('Done.')
