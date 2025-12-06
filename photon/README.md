# Photon (MVP)

This is a minimal MVP backend for Photon (file-based vector store and LLM integration via HuggingFace Inference API).

Quick start (PowerShell)

```powershell
cd D:\Photon\photon_initial\photon
# create and activate venv if not already active
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\.venv\Scripts\Activate.ps1

# install minimal deps
pip install --upgrade pip
pip install fastapi uvicorn requests python-dotenv nbformat weaviate-client numpy

# set HF token in environment (or create .env with HF_TOKEN)
# Open a new PowerShell and run: $env:HF_TOKEN = 'hf_xxx'

# run backend
uvicorn app.main:app --reload --port 8000
```

Notes:

# Photon (MVP)

This is a minimal MVP backend for Photon (file-based vector store and LLM integration via HuggingFace Inference API or local sentence-transformers fallback).

Quick Start (Windows PowerShell)

1. Open PowerShell and go to the project folder:

```
cd D:\Photon\photon_initial\photon
```

2. Activate the virtual environment (if you created one earlier):

```
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies (only if not already installed):

```
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

4. Start the backend (helper script will try to free port 8000 if needed):

```
.\scripts\start_app.ps1
```

5. Test the server in a new PowerShell window or browser:

```
curl http://127.0.0.1:8000/
# or using Python
python -c "import requests; print(requests.get('http://127.0.0.1:8000/').text)"
```

6. Example search test:

```
python -c "import requests; r=requests.post('http://127.0.0.1:8000/query/', json={'query':'MODIS surface reflectance 2015','top_k':3}); print(r.status_code); print(r.json())"
```

Notes
- Do not run the start script with `--reload` — reload spawns extra processes that can cause port conflicts.
- If you want to use Hugging Face remote models, set `HF_TOKEN` in your environment before starting the server. The app will use a local `sentence-transformers` model as a fallback when no token is set or remote calls fail.

Local embedding fallback (important):
- The service falls back to a local `sentence-transformers` model when `HF_TOKEN` is not provided or when remote calls fail. To use the fallback you must have `sentence-transformers` installed (already included in `requirements.txt`).
- Local models load into memory and can use several hundred megabytes of RAM depending on the model. For small/demo workloads the default `all-MiniLM-L6-v2` is lightweight (~100-300MB), but plan for more memory for larger models.
- If you expect production traffic, prefer using a remote embedding provider or a managed vector DB to avoid heavy memory use on the app server.

Files of interest
- `scripts/ingest_sample.py` — fetches NASA CMR collections and indexes embeddings into `data/vectors.json`.
- `app/routes/query.py` — search endpoint.
- `app/routes/workflow.py` — workflow generator endpoint.
- `data/demo_modis_notebook.ipynb` — demo notebook file you can open in Jupyter.
- `scripts/start_app.ps1` — helper to start the server on port 8000.
