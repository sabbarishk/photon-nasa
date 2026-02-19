"""
Embedding helper.

Behavior:
- Always uses local sentence-transformers model for fast, consistent embeddings.
- Model is cached after first load so subsequent calls are instant.
- If HF_TOKEN is set AND local model unavailable, falls back to HF remote API.
"""

import os
import requests
from typing import List, Optional

HF_TOKEN = os.getenv("HF_TOKEN")
HF_HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else None

# Cached local model (loaded once, reused for all calls)
_local_model = None


def _get_local_model():
    """Load and cache the local sentence-transformers model."""
    global _local_model
    if _local_model is None:
        from sentence_transformers import SentenceTransformer
        _local_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _local_model


def get_embedding(text: str, model: str = "sentence-transformers/all-MiniLM-L6-v2") -> List[float]:
    """Return embedding as list[float].

    Uses local sentence-transformers model for fast, consistent embeddings.
    The model is cached after first load so subsequent calls are near-instant.
    Falls back to HF remote API only if local model is unavailable.
    """
    # Always try local first - it's fast (cached), consistent, and free
    try:
        local = _get_local_model()
        emb = local.encode(text)
        return emb.tolist()
    except ImportError:
        pass  # sentence-transformers not installed, fall back to remote
    except Exception:
        pass  # any other local error, try remote

    # Fallback: HF remote (only if token set)
    if HF_TOKEN:
        candidates = [
            model,
            "sentence-transformers/all-mpnet-base-v2",
            "sentence-transformers/multi-qa-MiniLM-L6-cos-v1",
        ]
        for m in candidates:
            url = f"https://router.huggingface.co/embeddings/{m}"
            try:
                r = requests.post(url, headers=HF_HEADERS, json={"inputs": text}, timeout=15)
                r.raise_for_status()
                out = r.json()
                if isinstance(out, dict) and "embedding" in out:
                    return out["embedding"]
                if isinstance(out, list):
                    return out
            except Exception:
                continue

    raise RuntimeError("Embedding failed: install sentence-transformers or set HF_TOKEN")


def generate_code(prompt: str, model: str = "Salesforce/codegen-350M-multi", max_tokens: int = 1024) -> str:
    """Generate code/text using HF Router models endpoint. Returns generated text."""

    if not HF_TOKEN:
        raise RuntimeError("HF_TOKEN not set. Set HF_TOKEN to use remote code generation.")

    url = f"https://router.huggingface.co/models/{model}"
    payload = {"inputs": prompt, "parameters": {"max_new_tokens": max_tokens}}
    r = requests.post(url, headers=HF_HEADERS, json=payload, timeout=120)
    r.raise_for_status()
    out = r.json()

    # HF usually returns a list of results with 'generated_text'
    if isinstance(out, list) and len(out) > 0 and isinstance(out[0], dict) and "generated_text" in out[0]:
        return out[0]["generated_text"]
    if isinstance(out, dict) and "error" in out:
        raise RuntimeError(out["error"])
    return str(out)
