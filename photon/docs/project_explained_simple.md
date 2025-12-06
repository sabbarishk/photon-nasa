# Photon Project — Simple Explanation (No Jargon)

**What is Photon?**  
Photon helps scientists find NASA datasets by asking questions in plain English, then automatically creates a ready-to-run Python notebook that downloads and analyzes the data.

Think of it like this:  
- You ask: "Show me temperature data from MODIS 2015"  
- Photon finds the right datasets  
- Photon writes a notebook for you that loads the data and makes a chart  
- You just run the notebook and see results

---

## Project Structure (What Each Folder Does)

```
photon_initial/
├── photon/                    ← Main project folder (the "brain")
│   ├── app/                   ← Backend code (the server that answers requests)
│   │   ├── main.py            ← Entry point (starts the server)
│   │   ├── routes/            ← Different "doors" the server has:
│   │   │   ├── health.py      ← /health door (checks if server is alive)
│   │   │   ├── query.py       ← /query door (search for datasets)
│   │   │   ├── workflow.py    ← /workflow/generate door (makes notebooks)
│   │   ├── services/          ← Helper workers that do specific jobs:
│   │   │   ├── auth.py        ← Checks if you have a valid key to use the API
│   │   │   ├── embedding.py   ← Turns text into number-lists (embeddings)
│   │   │   ├── hf_api.py      ← Talks to Hugging Face (remote AI service)
│   │   │   ├── llm.py         ← Talks to language models (AI for code)
│   │   │   ├── nasa_api.py    ← Fetches NASA dataset info
│   │   │   ├── redis_rate_limiter.py ← Stops people from asking too much too fast
│   │   │   ├── vector_db.py   ← Stores and searches number-lists (embeddings)
│   │   │   ├── vector_store.py ← File or database storage for vectors
│   │   ├── templates/         ← Recipe cards for making notebooks:
│   │   │   ├── csv.txt        ← Recipe for CSV files
│   │   │   ├── netcdf.txt     ← Recipe for NetCDF files
│   ├── data/                  ← Storage area for small files:
│   │   ├── api_keys.json      ← List of valid keys people can use
│   │   ├── vectors.json       ← Stored dataset summaries (number-lists)
│   │   ├── generated_notebook.ipynb ← Example output notebook
│   │   ├── demo_modis_notebook.ipynb ← Pre-made demo notebook
│   ├── docs/                  ← Instructions and guides:
│   │   ├── auth_and_rate_limit.md ← How auth and rate limits work
│   │   ├── pilot_one_pager.md     ← Short pitch document
│   │   ├── redis_rate_limiter.md  ← How Redis rate limiter works
│   │   ├── vector_store_chroma.md ← How to use Chroma vector DB
│   ├── scripts/               ← Helper tools you can run:
│   │   ├── create_api_key.py     ← Makes a new API key
│   │   ├── generate_workflow.py  ← CLI tool to make notebooks
│   │   ├── ingest_sample.py      ← Fetches NASA data and stores it
│   │   ├── run_server.ps1        ← PowerShell script to start server
│   │   ├── start_app.ps1         ← Another PowerShell helper
│   │   ├── test_chroma_local.py  ← Tests Chroma database
│   │   ├── test_local_emb.py     ← Tests local embedding model
│   ├── tests/                 ← Automated checks to ensure code works:
│   │   ├── test_api.py           ← Tests API endpoints
│   │   ├── test_vector_store.py  ← Tests vector storage
│   ├── frontend/              ← (Future) Web page for users
│   ├── venv/                  ← Python packages installed here
│   ├── requirements.txt       ← List of Python packages needed
│   ├── README.md              ← Quick start guide
│   ├── docker-compose.yml     ← (Optional) Docker config
├── docker/                    ← Docker configs for services
│   ├── docker-compose.redis.yml ← Runs Redis database
├── .github/workflows/         ← Automated tests (CI/CD)
│   ├── ci.yml                 ← GitHub Actions config
```

---

## How It Works (Step-by-Step)

### When You Search for Datasets

1. **You ask a question** (e.g., "surface reflectance MODIS 2015")
2. **Server receives request** at `/query` route
3. **Embedding helper** turns your question into a number-list (like a fingerprint)
4. **Vector store** compares your fingerprint to stored dataset fingerprints
5. **Best matches returned** — you get a list of relevant datasets with scores

**Simple diagram:**
```
You → /query → embedding → vector_store → results → You
```

### When You Generate a Notebook

1. **You pick a dataset** and say what you want to analyze
2. **Server receives request** at `/workflow/generate`
3. **Template helper** picks the right recipe (CSV/NetCDF/etc.)
4. **LLM (optional)** polishes the code
5. **Notebook builder** wraps code into a `.ipynb` file
6. **You get the notebook** — ready to download and run

**Simple diagram:**
```
You → /workflow/generate → template → (LLM polish) → notebook JSON → You
```

---

## Key Files Explained

### Backend (Server)

**`app/main.py`**  
- The "front door" of the server  
- Starts FastAPI and registers all routes  
- Adds middleware for auth and rate limiting  
- When you run `uvicorn app.main:app`, this file starts the server

**`app/routes/query.py`**  
- Handles search requests  
- Takes your question → makes embedding → searches vector store → returns results  
- Endpoint: `POST /query/`

**`app/routes/workflow.py`**  
- Handles notebook generation requests  
- Takes dataset info → picks template → optionally calls LLM → returns notebook JSON  
- Endpoint: `POST /workflow/generate`

**`app/services/vector_store.py`**  
- Stores dataset summaries as number-lists (embeddings)  
- Can use a simple file (`vectors.json`) or a database (Chroma, Weaviate)  
- Provides `add(...)` to store and `search(...)` to find similar items

**`app/services/hf_api.py`**  
- Talks to Hugging Face (a free AI service)  
- Gets embeddings (number-lists) for text  
- Can generate code using AI models  
- Falls back to local models if remote fails

**`app/services/auth.py`**  
- Checks if requests have a valid API key  
- Keys are stored in `data/api_keys.json`  
- Protects the API from unauthorized use

**`app/services/redis_rate_limiter.py`**  
- Stops users from making too many requests too fast  
- Uses Redis (a fast database) to count requests  
- Limits: 120 requests per minute per key

### Scripts (Tools You Run)

**`scripts/create_api_key.py`**  
- Makes a new API key and saves it to `data/api_keys.json`  
- Run: `python scripts/create_api_key.py`

**`scripts/generate_workflow.py`**  
- Command-line tool to generate notebooks  
- Run: `python scripts/generate_workflow.py --dataset-url <URL> --dataset-format csv --variable <VAR>`

**`scripts/ingest_sample.py`**  
- Fetches NASA dataset descriptions from the web  
- Turns them into embeddings and saves to `vectors.json`  
- Run: `python -m scripts.ingest_sample --keyword MODIS --limit 10`

**`scripts/run_server.ps1`**  
- PowerShell helper to start the server  
- Run: `.\scripts\run_server.ps1` (or add `-SkipAuth` for dev mode)

### Data Files

**`data/vectors.json`**  
- Stores dataset summaries as embeddings  
- Each entry has: id, metadata, and embedding (number-list)  
- Used by the search function

**`data/api_keys.json`**  
- List of valid API keys  
- Each key has: key string, created date, limits

**`data/generated_notebook.ipynb`**  
- Example notebook created by `/workflow/generate`  
- You can open this in Jupyter and run it

### Config Files

**`requirements.txt`**  
- List of Python packages the project needs  
- Install with: `pip install -r requirements.txt`

**`docker-compose.redis.yml`**  
- Config to run Redis database in Docker  
- Redis is used for rate limiting

---

## How to Run (Simple Commands)

### 1. Install Python packages

```powershell
# Create a virtual environment (keeps packages separate)
cd D:\Photon\photon_initial\photon
python -m venv .\venv

# Activate it
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\venv\Scripts\Activate.ps1

# Install packages
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 2. Create an API key (optional, for production)

```powershell
python .\scripts\create_api_key.py
# Note the printed key
```

### 3. Start the server

```powershell
# Dev mode (no auth required)
.\scripts\run_server.ps1 -SkipAuth

# Or production mode (requires API key)
.\scripts\run_server.ps1
```

### 4. Test it

Open a browser and go to:
- `http://127.0.0.1:8000/` — should show `{"status":"photon backend OK"}`
- `http://127.0.0.1:8000/health` — should show `{"status":"ok"}`

### 5. Search for datasets (PowerShell)

```powershell
python -c "import requests; r=requests.post('http://127.0.0.1:8000/query/', json={'query':'MODIS surface reflectance 2015','top_k':3}); print(r.json())"
```

### 6. Generate a notebook (PowerShell)

```powershell
python .\scripts\generate_workflow.py --dataset-url "https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv" --dataset-format csv --variable "J-D"
```

---

## What Happens Inside (Behind the Scenes)

### When the server starts

1. `main.py` loads all configuration
2. Connects to vector store (file or database)
3. Loads API keys from `data/api_keys.json`
4. Sets up middleware (auth checker, rate limiter)
5. Registers routes (`/health`, `/query`, `/workflow/generate`)
6. Starts listening on port 8000

### When you search (`/query`)

1. Request comes in with `{"query": "MODIS 2015"}`
2. Middleware checks API key (if auth enabled)
3. `query.py` receives the request
4. Calls `hf_api.get_embedding(...)` to turn text into numbers
5. Calls `vector_store.search(...)` to find similar datasets
6. Returns top matches as JSON

### When you generate a notebook (`/workflow/generate`)

1. Request comes in with dataset URL, format, and variable
2. Middleware checks API key
3. `workflow.py` receives the request
4. Picks the right template (CSV, NetCDF, etc.)
5. Fills in the template with dataset details
6. (Optional) Calls LLM to polish the code
7. Wraps code into notebook JSON format
8. Returns notebook as JSON (you save as `.ipynb`)

---

## Glossary (Simple Definitions)

**API** — A way for programs to talk to each other. Like a waiter taking your order to the kitchen.

**Embedding** — A number-list that represents text. Similar texts get similar numbers. Like fingerprints for words.

**Vector** — Just another word for a list of numbers (an embedding).

**Vector Store** — A place that stores embeddings and can find similar ones quickly.

**Middleware** — Code that runs before your request reaches the main handler. Like a security guard checking tickets.

**Rate Limiter** — A tool that stops people from making too many requests too fast. Prevents abuse.

**Jupyter Notebook** — A file (`.ipynb`) that contains code, text, and results. Scientists use it to document their work.

**FastAPI** — A Python tool for building web servers quickly and easily.

**Redis** — A super-fast database used for counting and caching.

**Chroma/Weaviate** — Databases designed specifically for storing and searching embeddings.

**LLM (Large Language Model)** — An AI that can understand and generate text/code. Like ChatGPT or Claude.

**HuggingFace** — A company that provides free AI models and services.

**Docker** — A tool that runs programs in isolated containers. Like a virtual computer inside your computer.

**CI/CD** — Automated testing that runs every time you change code. Ensures nothing breaks.

---

## What's Done vs. What's Left

### ✅ Done (You Can Use These Now)

- Backend server with routes for health, search, and workflow generation
- API key authentication and rate limiting
- Vector storage (file-based or Chroma database)
- Embedding generation (Hugging Face + local fallback)
- Notebook generation with templates
- Scripts to create keys, ingest data, and generate notebooks
- Tests and CI setup
- Documentation

### 🔨 Not Done Yet (Future Work)

- Web UI (frontend) for non-technical users
- Docker deployment configs
- Advanced monitoring and metrics
- More dataset templates (HDF5, FITS)
- Automated dataset updates
- User accounts and billing

---

## Next Steps (For You)

1. **Try running the server** — use `.\scripts\run_server.ps1 -SkipAuth`
2. **Try a search** — use the PowerShell command from section "How to Run"
3. **Generate a notebook** — use `generate_workflow.py` script
4. **Open the notebook** — open the generated `.ipynb` file in Jupyter or VS Code
5. **Read the other docs** — check `docs/` folder for more details

---

**Questions?**  
If anything is unclear, ask! This is a complex project, but we've broken it down into simple pieces. Each piece does one job, and they work together to help scientists find and analyze NASA data faster.
