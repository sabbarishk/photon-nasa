# Technical Architecture Guide

## Photon-NASA System Design and Components

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Frontend Architecture](#frontend-architecture)
3. [Backend Architecture](#backend-architecture)
4. [Embedding System](#embedding-system)
5. [Vector Store](#vector-store)
6. [Data Flow](#data-flow)
7. [Performance Optimization](#performance-optimization)

---

## 1. SYSTEM ARCHITECTURE

### High-Level Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                          USER                                  │
│               (Browser: Chrome, Firefox, Safari)               │
└──────────────────────────┬─────────────────────────────────────┘
                           │ HTTPS/HTTP
                           ▼
┌────────────────────────────────────────────────────────────────┐
│                   FRONTEND (React SPA)                         │
│  - Port: 5173 (dev) / 80 (prod)                               │
│  - Components: Hero, Search, WorkflowGenerator                 │
│  - Services: API client (Axios)                                │
│  - State: Context API                                          │
└──────────────────────────┬─────────────────────────────────────┘
                           │ REST API (JSON)
                           ▼
┌────────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI)                           │
│  - Port: 8000                                                  │
│  - Routes: /query, /workflow, /execute, /health               │
│  - Middleware: CORS, Auth, Rate Limiting, Logging             │
└──────────┬────────────────────────┬────────────────────────────┘
           │                        │
           ▼                        ▼
┌────────────────────┐    ┌────────────────────────┐
│   EMBEDDING        │    │   WORKFLOW             │
│   SYSTEM           │    │   GENERATOR            │
│                    │    │                        │
│ - Local Model      │    │ - Jinja2 Templates     │
│   (all-MiniLM)     │    │   csv.txt              │
│ - Thread-safe      │    │   netcdf.txt           │
│   caching          │    │   hdf5.txt             │
│ - 384-dim vectors  │    │   json.txt             │
│ - Sub-100ms        │    │ - nbformat builder     │
└──────────┬─────────┘    └────────────────────────┘
           │
           ▼
┌────────────────────────────────────────────────────────────────┐
│                   VECTOR STORE                                 │
│  - File Backend (default): vectors.json                        │
│  - Chroma Backend (optional): DuckDB + Parquet                 │
│  - In-memory cache for performance                             │
└────────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Layer | Technologies |
|-------|-------------|
| **Frontend** | React 18, Vite, Tailwind CSS, Axios |
| **Backend** | FastAPI, Uvicorn, Pydantic |
| **ML/AI** | sentence-transformers (all-MiniLM-L6-v2) |
| **Data** | NumPy, pandas, nbformat, Jinja2 |
| **Optional** | Redis (rate limiting), ChromaDB (vectors) |

---

## 2. FRONTEND ARCHITECTURE

### Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Hero.jsx              # Landing page
│   │   ├── Search.jsx            # Dataset search interface
│   │   ├── WorkflowGenerator.jsx # Notebook generator
│   │   ├── Navbar.jsx            # Navigation
│   │   └── Footer.jsx            # Footer
│   ├── context/
│   │   └── DatasetContext.jsx    # Shared state
│   ├── services/
│   │   └── api.js                # API client
│   ├── App.jsx                   # Main app
│   └── main.jsx                  # Entry point
├── public/
├── index.html
├── vite.config.js
├── tailwind.config.js
└── package.json
```

### Component Responsibilities

#### **Hero.jsx**
Landing page with project overview and call-to-action.

#### **Search.jsx**
```javascript
// Key functionality:
- Natural language search input
- Results display with relevance scores
- "Generate Workflow" button per result
- Error handling for failed searches
```

#### **WorkflowGenerator.jsx**
```javascript
// Key functionality:
- Auto-populated form (URL, format, variable)
- Notebook generation
- Code preview
- Download .ipynb
- Run & Visualize (execution)
```

### State Management

**DatasetContext Pattern:**
```javascript
const DatasetContext = createContext()

export function DatasetProvider({ children }) {
  const [selectedDataset, setSelectedDataset] = useState(null)
  
  const selectDataset = (dataset) => {
    setSelectedDataset(dataset)
  }
  
  return (
    <DatasetContext.Provider value={{ selectedDataset, selectDataset }}>
      {children}
    </DatasetContext.Provider>
  )
}
```

### API Service Layer

```javascript
// services/api.js
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' }
})

export const searchDatasets = async (query, topK = 5) => {
  const response = await api.post('/query/', { query, top_k: topK })
  return response.data
}

export const generateWorkflow = async (datasetUrl, format, variable, title) => {
  const response = await api.post('/workflow/generate', {
    dataset_url: datasetUrl,
    dataset_format: format,
    variable,
    title: title || 'Generated Workflow'
  })
  return response.data
}

export const executeNotebook = async (code, timeout = 60) => {
  const response = await api.post('/execute/notebook', { code, timeout })
  return response.data
}
```

---

## 3. BACKEND ARCHITECTURE

### Project Structure

```
photon/
├── app/
│   ├── main.py                   # FastAPI app entry
│   ├── routes/
│   │   ├── query.py              # POST /query/
│   │   ├── workflow.py           # POST /workflow/generate
│   │   ├── execute.py            # POST /execute/notebook
│   │   └── health.py             # GET /health
│   ├── services/
│   │   ├── hf_api.py             # Embedding generation
│   │   ├── vector_store.py       # Vector storage & search
│   │   ├── nasa_api.py           # NASA CMR client
│   │   ├── auth.py               # API key validation
│   │   └── redis_rate_limiter.py # Rate limiting
│   └── templates/
│       ├── csv.txt               # CSV notebook template
│       ├── netcdf.txt            # NetCDF template
│       ├── hdf5.txt              # HDF5 template
│       └── json.txt              # JSON template
├── data/
│   ├── vectors.json              # Vector store (file backend)
│   └── api_keys.json             # API keys (if auth enabled)
├── scripts/
│   ├── bulk_ingest.py            # Ingest 34 datasets
│   ├── ingest_sample.py          # NASA CMR ingestion
│   └── run_server.ps1            # Server startup
└── requirements.txt
```

### Main Application (main.py)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import threading
import logging

from app.routes import query, workflow, health, execute

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('photon')

app = FastAPI(
    title="Photon",
    description="Natural language query layer for NASA open data",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pre-warm embedding model on startup
def _warmup_embedding_model():
    try:
        logger.info("Pre-warming embedding model...")
        from app.services.hf_api import get_embedding
        get_embedding("warmup photon nasa")
        logger.info("Embedding model ready.")
    except Exception as e:
        logger.warning(f"Embedding warmup failed (non-fatal): {e}")

@app.on_event("startup")
async def startup_event():
    threading.Thread(target=_warmup_embedding_model, daemon=True).start()

# Register routes
app.include_router(query.router, prefix="/query", tags=["query"])
app.include_router(workflow.router, prefix="/workflow", tags=["workflow"])
app.include_router(execute.router, prefix="/execute", tags=["execute"])
app.include_router(health.router, tags=["health"])

@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "Photon NASA Data API",
        "version": "1.0.0",
        "docs": "/docs"
    }
```

### Search Endpoint (routes/query.py)

```python
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

from app.services.hf_api import get_embedding
from app.services.vector_store import VectorStore

router = APIRouter()
vs = VectorStore("data/vectors.json")

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5

class QueryResponse(BaseModel):
    query: str
    results: List[dict]

@router.post("/", response_model=QueryResponse)
def search(req: QueryRequest):
    """Semantic search over NASA datasets."""
    # Generate embedding for query
    emb = get_embedding(req.query)
    
    # Search vector store
    results = vs.search(emb, top_k=req.top_k)
    
    return {
        "query": req.query,
        "results": results
    }
```

### Workflow Generation (routes/workflow.py)

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
from jinja2 import Template
from uuid import uuid4

router = APIRouter()

class WorkflowRequest(BaseModel):
    dataset_url: str
    dataset_format: str
    variable: str
    title: str = "Generated Workflow"

@router.post("/generate")
async def generate_workflow(request: WorkflowRequest):
    """Generate Jupyter notebook for dataset analysis."""
    try:
        # Load template based on format
        template_path = Path(__file__).parent.parent / "templates" / f"{request.dataset_format.lower()}.txt"
        
        if not template_path.exists():
            raise HTTPException(
                status_code=400,
                detail=f"No template for format: {request.dataset_format}"
            )
        
        with open(template_path, "r", encoding="utf-8") as f:
            template_str = f.read()
        
        # Render template with user's data
        template = Template(template_str)
        code = template.render(
            dataset_url=request.dataset_url,
            variable=request.variable,
            title=request.title
        )
        
        # Clean BOM and whitespace
        code = code.lstrip('\ufeff\ufbf0\ufbf1\ufbf2').strip()
        
        # Build Jupyter notebook JSON
        notebook = {
            "cells": [{
                "cell_type": "code",
                "execution_count": None,
                "id": str(uuid4())[:8],
                "metadata": {},
                "outputs": [],
                "source": code.split('\n')
            }],
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3"
                }
            },
            "nbformat": 4,
            "nbformat_minor": 5
        }
        
        return {
            "notebook": notebook,
            "preview": code[:500],
            "format": request.dataset_format
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate workflow: {str(e)}"
        )
```

---

## 4. EMBEDDING SYSTEM

### Implementation (services/hf_api.py)

```python
"""
Embedding helper.

STRATEGY:
- PRIMARY: Local sentence-transformers model (cached in memory)
- FALLBACK: Hugging Face remote API (only if local unavailable)

Why local-first?
- 20-50x faster (sub-100ms vs 2-5s)
- No external dependency for critical path
- No rate limits
- Consistent results
- Free (no API token needed)
"""

import os
import requests
import threading
from typing import List

HF_TOKEN = os.getenv("HF_TOKEN")
HF_HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else None

# Global cached model (loaded once, reused forever)
_local_model = None
_model_lock = threading.Lock()

def _get_local_model():
    """Load and cache the sentence-transformers model.
    
    Thread-safe lazy initialization ensures model is loaded exactly once,
    even under concurrent requests.
    """
    global _local_model
    if _local_model is not None:
        return _local_model
    
    with _model_lock:
        if _local_model is None:
            from sentence_transformers import SentenceTransformer
            _local_model = SentenceTransformer("all-MiniLM-L6-v2")
    
    return _local_model

def get_embedding(text: str, model: str = "sentence-transformers/all-MiniLM-L6-v2") -> List[float]:
    """Return 384-dimensional embedding vector.
    
    Uses cached local model for speed and reliability.
    Falls back to HF remote API only if local model unavailable.
    """
    # Try local first (99.9% of production usage)
    try:
        local_model = _get_local_model()
        emb = local_model.encode(text)
        return emb.tolist()
    except Exception as local_error:
        pass
    
    # Fallback: HF remote API (only if token set and local failed)
    if HF_TOKEN:
        url = f"https://router.huggingface.co/embeddings/{model}"
        try:
            r = requests.post(
                url,
                headers=HF_HEADERS,
                json={"inputs": text},
                timeout=15
            )
            r.raise_for_status()
            out = r.json()
            
            if isinstance(out, dict) and "embedding" in out:
                return out["embedding"]
            if isinstance(out, list):
                return out
        except Exception:
            pass
    
    raise RuntimeError(
        "Embedding failed: install sentence-transformers or set HF_TOKEN"
    )
```

### Performance Characteristics

| Metric | Local Model | Remote API |
|--------|-------------|------------|
| First load | 1.2s (model download) | N/A |
| Subsequent calls | Sub-100ms (cached) | 2-5s per call |
| External dependency | None | HF API availability |
| Rate limits | None | Yes (tiered by token) |
| Consistency | Guaranteed | Subject to API changes |
| Cost | Free | Free tier + paid tiers |

---

## 5. VECTOR STORE

### Implementation (services/vector_store.py)

```python
import os
import json
import numpy as np

class VectorStore:
    """Vector store with pluggable backends.
    
    Backends:
    - 'file': JSON file (default, good for under 10k vectors)
    - 'chroma': ChromaDB (production, handles millions)
    """
    
    def __init__(self, path: str = "data/vectors.json", backend: str = None):
        self.backend = backend or os.getenv('VECTOR_STORE_BACKEND', 'file')
        self.path = os.path.normpath(path)
        self._cache = None
        
        if self.backend == 'file':
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            if not os.path.exists(self.path):
                with open(self.path, 'w', encoding='utf-8') as f:
                    json.dump([], f)
            # Pre-load into memory at startup
            self._cache = self._load_from_disk()
    
    def _load_from_disk(self):
        """Read vectors from JSON file."""
        with open(self.path, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    
    def _load(self):
        """Load vectors (uses cache for file backend)."""
        if self.backend == 'file':
            if self._cache is not None:
                return self._cache
            return self._load_from_disk()
    
    def _save(self, objects):
        """Save vectors to disk."""
        if self.backend == 'file':
            with open(self.path, 'w', encoding='utf-8') as f:
                json.dump(objects, f, ensure_ascii=False, indent=2)
            self._cache = objects
    
    def add(self, id: str, meta: dict, embedding: list):
        """Store a document with its embedding."""
        if self.backend == 'file':
            objs = self._load()
            objs.append({"id": id, "meta": meta, "embedding": embedding})
            self._save(objs)
    
    def search(self, embedding: list, top_k: int = 5):
        """Find top_k most similar documents.
        
        Uses vectorized NumPy operations for speed.
        """
        if self.backend == 'file':
            objs = self._load()
            if not objs:
                return []
            
            # Vectorized cosine similarity
            query_vec = np.array(embedding, dtype=float)
            query_norm = np.linalg.norm(query_vec)
            
            valid_objs = [o for o in objs if o.get("embedding")]
            if not valid_objs:
                return []
            
            # Stack all embeddings into matrix for bulk computation
            matrix = np.array([o["embedding"] for o in valid_objs], dtype=float)
            norms = np.linalg.norm(matrix, axis=1)
            
            # Compute cosine similarities
            with np.errstate(divide='ignore', invalid='ignore'):
                scores = np.where(
                    (norms > 0) & (query_norm > 0),
                    matrix.dot(query_vec) / (norms * query_norm),
                    0.0
                )
            
            # Get top_k indices
            top_indices = np.argpartition(
                scores,
                -min(top_k, len(scores))
            )[-min(top_k, len(scores)):]
            top_indices = top_indices[np.argsort(scores[top_indices])[::-1]]
            
            # Build results
            results = []
            for idx in top_indices:
                o = valid_objs[idx]
                results.append({
                    "id": o.get("id"),
                    "score": float(scores[idx]),
                    "meta": o.get("meta")
                })
            
            return results
```

### Cosine Similarity Math

```python
def cosine_similarity(a, b):
    """
    Compute cosine similarity between two vectors.
    
    Formula: similarity(A, B) = (A · B) / (||A|| × ||B||)
    
    Where:
    - A · B = dot product = sum of (A[i] × B[i])
    - ||A|| = magnitude = sqrt(sum of A[i]²)
    
    Result: -1 to 1
    - 1.0  = identical direction (very similar)
    - 0.5  = moderate similarity
    - 0.0  = perpendicular (unrelated)
    - -1.0 = opposite direction (opposite meaning)
    """
    a = np.array(a, dtype=float)
    b = np.array(b, dtype=float)
    
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 0.0
    
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
```

---

## 6. DATA FLOW

### Complete End-to-End Example

**Scenario: User searches for "GISS temperature data"**

#### Step 1: User Input
```
User types: "GISS temperature data"
Clicks: Search button
```

#### Step 2: Frontend Sends Request
```javascript
// Search.jsx
const handleSearch = async (e) => {
  e.preventDefault()
  setLoading(true)
  
  const data = await searchDatasets("GISS temperature data", 5)
  
  setResults(data.results)
  setLoading(false)
}
```

**HTTP Request:**
```http
POST http://localhost:8000/query/
Content-Type: application/json

{
  "query": "GISS temperature data",
  "top_k": 5
}
```

#### Step 3: Backend Processes Request
```python
# routes/query.py
@router.post("/")
def search(req: QueryRequest):
    # Generate embedding (cached model, sub-100ms)
    emb = get_embedding(req.query)
    # emb = [0.234, -0.451, 0.678, ..., -0.089]  # 384 numbers
    
    # Search vector store
    results = vs.search(emb, top_k=req.top_k)
    
    return {"query": req.query, "results": results}
```

#### Step 4: Embedding Generation
```python
# services/hf_api.py
def get_embedding(text):
    model = _get_local_model()  # Cached, instant return
    emb = model.encode("GISS temperature data")
    return emb.tolist()
```
*Time: Sub-100ms*

#### Step 5: Vector Search
```python
# services/vector_store.py
def search(self, embedding, top_k=5):
    # Load cached vectors
    objects = self._cache  # In-memory
    
    # Vectorized cosine similarity
    query_vec = np.array(embedding)
    matrix = np.array([o["embedding"] for o in objects])
    scores = matrix.dot(query_vec) / (norms * query_norm)
    
    # Get top 5
    top_indices = np.argpartition(scores, -5)[-5:]
    
    return [{"id": objects[idx]["id"], "score": float(scores[idx]), "meta": objects[idx]["meta"]} for idx in top_indices]
```
*Time: 50-100ms*

#### Step 6: Response Returned
```json
{
  "query": "GISS temperature data",
  "results": [
    {
      "id": "giss-global-temp",
      "score": 0.92,
      "meta": {
        "title": "GISS Global Temperature Analysis",
        "dataset_url": "https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv",
        "format": "CSV",
        "variable": "J-D"
      }
    }
  ]
}
```

**Total time: 150-250ms from query to displayed results**

---

## 7. PERFORMANCE OPTIMIZATION

### Current Performance Metrics

| Operation | Time (MVP) | Target (Production) |
|-----------|------------|---------------------|
| Embedding generation | Sub-100ms | Under 50ms |
| Vector search (34 vectors) | 28-55ms | Under 25ms |
| Workflow generation | 2-5s | Under 1s |
| Total search time | 150-250ms | Under 100ms |

### Optimization Strategies

#### **Embedding System**
- **Local model caching** - Eliminates 2-5s API latency
- **Pre-warming on startup** - First search is instant
- **Thread-safe loading** - Prevents race conditions

**Result: 20-50x performance improvement**

#### **Vector Search**
- **Vectorized NumPy operations** - Batch similarity computation
- **In-memory caching** - No disk I/O per search
- **Efficient top-k selection** - `np.argpartition` instead of full sort

**Result: 10-100x faster for large datasets**

#### **Frontend Optimization**
- **Vite for instant HMR** - Under 50ms updates during development
- **Code splitting** - Lazy load components
- **Tailwind CSS purging** - Remove unused styles

**Build output:**
- HTML: ~3KB (gzipped)
- CSS: ~12KB (gzipped)
- JS: ~150KB (gzipped, includes React)

---

*For API documentation, see [API Reference](02_API_REFERENCE.md)*  
*For deployment instructions, see [Deployment Guide](03_DEPLOYMENT_GUIDE.md)*
