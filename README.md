# Photon

**Open-source conversational data analyst.**  
Upload any CSV or Excel file, ask questions in plain English, and get a complete KPI dashboard with real executed results — not AI guesses.

> Self-hostable alternative to Julius AI, ChatCSV, and Retool AI. MIT license. No signup required.

---

## Why Photon

Every AI data tool either generates code you have to run yourself, or lives behind a paywall. Photon executes your analysis on AWS Lambda and returns real computed results in a conversational interface you can self-host for free.

- **Real execution** — analysis code runs on AWS Lambda. Every number in your dashboard comes from actual computation against your data, not LLM hallucination.
- **Conversational** — ask follow-ups. Each turn builds on the previous analysis. "Show me by department." "Why is this dropping?" "Which operator has the most redos?" Every follow-up re-executes against real data.
- **Self-hostable** — git clone and run. No SaaS subscription, no data leaving your infrastructure (except the Lambda call), MIT license.
- **Full dashboard** — KPI cards, multi-panel charts, AI insight narrative, anomaly detection. Not a single chart. A complete analyst output.

![Photon analysis workspace](docs/screenshot-upload.png)

---

## Architecture

```
User question + CSV / Excel / URL
        │
        ▼
┌───────────────────┐
│   FastAPI Backend │  Python 3.11
└────────┬──────────┘
         │
         ├──▶ Data Profiler
         │       Schema extraction, type detection,
         │       null analysis, KPI candidate identification
         │
         ├──▶ ChromaDB RAG
         │       Retrieves methodology playbook by data type
         │       (tabular / time_series / wide_format)
         │
         ├──▶ Anthropic Claude API  (claude-sonnet-4-6)
         │       Pass 1: grounded code generation
         │               (profile + playbook + conversation history)
         │       Pass 2: AI insight narrative generation
         │       Pass 3: follow-up question suggestions
         │
         ├──▶ AWS Lambda  (sandboxed execution)
         │       Real computation, real results
         │       pandas / numpy / matplotlib in isolated environment
         │       No in-process exec() — Lambda only
         │
         └──▶ Dashboard Response
                 KPI cards  ·  Multi-panel charts
                 Insight narrative  ·  Anomaly callouts
                 Follow-up suggestions
```

![4-panel dashboard](docs/screenshot-dashboard.png)

Conversation history is passed client-side on every request. The backend is stateless — no sessions, no Redis, no server-side user state. This is what makes it self-hostable: git clone and run.

---

## Tech stack

| Layer | Technology |
|---|---|
| LLM | Anthropic Claude API (`claude-sonnet-4-6`) |
| RAG | ChromaDB (persistent, cosine similarity, HNSW) · sentence-transformers (`all-MiniLM-L6-v2`) |
| Execution | AWS Lambda (Python 3.11, `photon-data-science` layer, 512 MB, 30s timeout) |
| Storage | AWS S3 (`photon-analysis-storage`, us-east-1) |
| Backend | Python 3.11 · FastAPI |
| Frontend | React 18 · Vite · Tailwind CSS |
| Auth | API key middleware (`PHOTON_SKIP_AUTH=1` for local dev) |

---

## Running locally

### 1. Clone and set up Python

```bash
git clone https://github.com/sabbarishk/photon-nasa.git
cd photon-nasa

cd photon
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

### 2. Set up frontend

```bash
cd frontend
npm install
```

### 3. Configure environment

```bash
cp photon/.env.example photon/.env
```

Edit `photon/.env`:

```env
ANTHROPIC_API_KEY=sk-ant-...
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1
PHOTON_SKIP_AUTH=1
```

The IAM user needs only `lambda:InvokeFunction` on the `photon-code-executor` function.

### 4. Deploy AWS Lambda

The Lambda function executes the generated analysis code in a sandboxed environment.

```bash
# Create the data science layer (pandas, numpy, matplotlib)
cd aws
.\create_layer.ps1          # Windows PowerShell

# Deploy the Lambda function
aws lambda create-function \
  --function-name photon-code-executor \
  --runtime python3.11 \
  --role arn:aws:iam::YOUR_ACCOUNT:role/photon-lambda-role \
  --handler lambda_function.handler \
  --timeout 30 \
  --memory-size 512 \
  --zip-file fileb://function.zip
```

See `aws/README.md` for full Lambda setup instructions.

### 5. Load ChromaDB playbooks

```bash
cd photon
python scripts/load_playbooks.py
```

### 6. Start both servers

```bash
# Terminal 1 — backend
cd photon
$env:PHOTON_SKIP_AUTH="1"    # PowerShell
uvicorn app.main:app --reload --app-dir photon

# Terminal 2 — frontend
cd frontend
npm run dev
```

Open [http://localhost:5173](http://localhost:5173).

---

## Try the demo

Without uploading anything, click **Try Demo** on the landing page or the navbar. This loads a synthetic manufacturing quality dataset (500 rows, Jan–Dec 2024) with realistic patterns:

- Q3 higher redo rates (summer heat affecting quality)
- Aging equipment (EQ-007, EQ-011) with elevated defect rates
- Operator-level performance differences (OP-003, OP-018)
- Department scrap rate comparison
- Client order quality breakdown

Example questions to try:
- "What are the key quality trends?"
- "Which department has the highest redo rate?"
- "Show me defect rates by equipment"
- "Are there any anomalies in the night shift data?"

---

## Project structure

```
photon/
  app/
    routes/        FastAPI route handlers (workflow, upload, demo, health)
    services/      Core services: LLM, Lambda executor, ChromaDB, profiler
  data/
    playbooks/     RAG methodology documents (tabular, time_series, wide_format)
    demo/          Synthetic manufacturing demo dataset
  scripts/         Data generation, ChromaDB ingestion, utility scripts
frontend/
  src/
    pages/         Landing, Workspace
    components/    KPICard, Badge, Skeleton, SuggestionChip, StepProgress
    services/      API client (analyzeData, uploadFile, pingBackend)
aws/               Lambda function code and layer build scripts
docs/              Architecture decisions (DECISIONS.md), progress log (PROGRESS.md)
```

---

## License

MIT — use it, fork it, self-host it.
