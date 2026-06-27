# Photon — AI Data Analysis Assistant

Ask a question about your data in plain English. Photon profiles the dataset, retrieves the right analysis methodology via RAG, generates grounded Python code, executes it in a sandboxed AWS Lambda, and returns real results — not hallucinated output.

## What it does

Paste any public CSV URL and ask a question. Photon runs a data profiler to detect the dataset type (tabular, time series, wide format) and extract column schema. It uses that classification to retrieve a matching methodology playbook from ChromaDB. That methodology grounds the prompt sent to the Anthropic Claude API, which generates analysis code specific to the data structure — not generic pandas defaults. The code runs in AWS Lambda (no network access, strict memory and time limits), and the real output — stdout, a chart, and the generated code — comes back to the browser.

## Architecture

```
User question + CSV URL
→ Data Profiler          (type detection, schema, null analysis)
→ ChromaDB RAG           (methodology playbook retrieval by data type)
→ Anthropic Claude API   (grounded Python code generation)
→ AWS Lambda             (sandboxed execution, no network, 15s timeout)
→ Real results + chart   (stdout, base64 PNG, generated code visible)
```

## Tech stack

- **Backend:** Python 3.11, FastAPI
- **Embeddings:** sentence-transformers (all-MiniLM-L6-v2), local inference
- **Vector store:** ChromaDB (persistent, cosine similarity, HNSW index)
- **LLM:** Anthropic Claude API (claude-sonnet-4-6)
- **Execution sandbox:** AWS Lambda (no network, 256 MB RAM, 15 s timeout)
- **Frontend:** React 18 + Vite, Tailwind CSS

## Running locally

```bash
# 1. Clone and configure
git clone https://github.com/sabbarishk/photon.git
cd photon
cp .env.example .env
# Edit .env — fill in ANTHROPIC_API_KEY, AWS_ACCESS_KEY_ID,
# AWS_SECRET_ACCESS_KEY, AWS_REGION

# 2. Install backend dependencies
cd photon
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux
pip install -r requirements.txt

# 3. Start the API server (from repo root)
cd ..
uvicorn app.main:app --reload --app-dir photon
# → http://localhost:8000

# 4. Start the frontend (separate terminal)
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

> `PHOTON_SKIP_AUTH=1` in `.env` bypasses API key auth for local development. Remove it before deploying.

Quick test via curl:

```bash
curl -s -X POST http://localhost:8000/workflow/generate \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the trend over time?",
       "source": "https://people.sc.fsu.edu/~jburkardt/data/csv/airtravel.csv"}'
```

## Project structure

| Directory | Contents |
|-----------|----------|
| `photon/` | FastAPI backend — routes, profiler, ChromaDB client, LLM service, Lambda executor |
| `frontend/` | React + Vite UI — three-state flow: input → loading → results |
| `data/` | Methodology playbooks (tabular, time\_series, wide\_format) loaded into ChromaDB |
| `docker/` | Sandbox Dockerfile (retained for reference; execution migrated to Lambda) |
| `aws/` | IAM least-privilege setup for Lambda invocation |
| `docs/` | `DECISIONS.md` (ADR log), `PROGRESS.md` (session history) |
