"""
Minimal HuggingFace Inference API helper.

Behavior:
- Try several Hugging Face router embedding models if `HF_TOKEN` is set.
- If remote calls fail or `HF_TOKEN` is not set, fall back to a local
  `sentence-transformers` model (if installed).
"""

import os
import requests
from typing import List, Optional

HF_TOKEN = os.getenv("HF_TOKEN")
HF_HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else None


def get_embedding(text: str, model: str = "sentence-transformers/all-MiniLM-L6-v2") -> List[float]:
    """Return embedding as list[float].

    Tries several remote models via the Hugging Face router. If all remote
    attempts fail or HF_TOKEN is not set, tries a local sentence-transformers
    model as a fallback.
    """

    candidates = [
        model,
        "sentence-transformers/all-mpnet-base-v2",
        "sentence-transformers/multi-qa-MiniLM-L6-cos-v1",
        "text-embedding-3-small",
    ]

    out: Optional[object] = None
    last_exc: Optional[Exception] = None

    # Try remote router embeddings only if we have a token
    if HF_TOKEN:
        for m in candidates:
            url = f"https://router.huggingface.co/embeddings/{m}"
            try:
                r = requests.post(url, headers=HF_HEADERS, json={"inputs": text}, timeout=60)
                r.raise_for_status()
                out = r.json()
                break
            except Exception as e:
                # Save last exception and try next candidate
                last_exc = e
                continue

    # If remote didn't work or HF_TOKEN absent, try a local model
    if out is None:
        try:
            from sentence_transformers import SentenceTransformer

            local_model = SentenceTransformer("all-MiniLM-L6-v2")
            emb = local_model.encode(text)
            # SentenceTransformer returns numpy array
            return emb.tolist()
        except Exception as e:
            # If we have a last remote exception, surface it for debugging
            if last_exc:
                raise last_exc
            raise RuntimeError("Embedding failed and no fallback available") from e

    # Parse HF router response
    if isinstance(out, dict) and "embedding" in out:
        return out["embedding"]
    if isinstance(out, list):
        return out  # some models return a direct list
    raise RuntimeError(f"Unexpected HF embeddings response: {out}")


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
