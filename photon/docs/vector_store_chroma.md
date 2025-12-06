Chroma Vector Store

This project can use `chromadb` as a backend for the vector store. The default remains the file-backed store.

Install chromadb (already added to `requirements.txt`) into your venv:

```powershell
Set-Location .\photon
python -m pip install --upgrade pip
python -m pip install chromadb
```

Run the server using the Chroma backend with a persistent directory (recommended for pilots):

```powershell
# from repo root; ensure PYTHONPATH points to the photon package
$env:PYTHONPATH = Join-Path (Get-Location).Path 'photon'
$env:VECTOR_STORE_BACKEND = 'chroma'
$env:CHROMA_PERSIST_DIR = (Join-Path (Get-Location).Path 'photon\data\chroma')
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Notes
- The adapter uses an in-process Chroma client with `duckdb+parquet` persistence in the directory set by `CHROMA_PERSIST_DIR`.
- For production you may prefer a managed vector DB or a dedicated Chroma server; this adapter is suitable for pilots and local persistence.
