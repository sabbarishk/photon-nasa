#!/usr/bin/env python3
"""Quick test for local sentence-transformers model.
Run from project root: python .\scripts\test_local_emb.py
"""
import sys
try:
    from sentence_transformers import SentenceTransformer
except Exception as e:
    print("IMPORT_ERROR", e)
    sys.exit(2)

try:
    m = SentenceTransformer("all-MiniLM-L6-v2")
    v = m.encode("hello world")
    print("OK", "len=", len(v))
except Exception as e:
    print("MODEL_ERROR", e)
    sys.exit(3)
