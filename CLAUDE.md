# Photon — project memory (v2)

This file is read automatically at the start of every Claude Code session.
Rules and facts only. Plans go in PROGRESS.md. Rationale goes in DECISIONS.md.
EVERY SESSION: use Claude Sonnet 4.6 HIGH. No exceptions.

---

## What Photon is — locked, do not deviate

Photon is an open-source, self-hostable conversational data analyst.

The user uploads a CSV or Excel file (or pastes a public URL), asks a
question in plain English, and gets back a complete KPI dashboard with
multiple metrics, trend charts, anomaly callouts, and an AI-written
insight narrative. The conversation continues — each follow-up message
refines, extends, or reframes the analysis. Every turn re-executes against
real data. Nothing is hallucinated. Output builds progressively into a
full dashboard.

This is the open-source alternative to Julius AI, Retool AI, and ChatCSV.
That is the GitHub star strategy. Self-hostable, free, professional.

---

## The two pillars — BOTH must be built, not planned

### Pillar 1 — Conversational AI Analysis (MOST IMPORTANT)
This is the core of the project. The LLM RAG pipeline is the heart.

Full pipeline per conversation turn:
1. Data ingestion: CSV upload, Excel upload (.xlsx), public URL
2. Data profiler: type detection, schema extraction, null analysis,
   KPI candidates identified automatically
3. ChromaDB RAG: retrieves analysis methodology playbook by data type
   (tabular, time_series, wide_format)
4. Conversation memory: full message history passed as context every turn
5. LLM generation (Anthropic claude-sonnet-4-6): grounded in profile +
   methodology + conversation history + user's specific question
6. AWS Lambda execution: sandboxed, real results, not hallucinated
7. Dashboard output: KPI cards + multi-panel charts + AI insight narrative
8. Iterative refinement: user follow-up triggers full pipeline again,
   building on previous analysis

### Pillar 2 — Data Engineering Pipeline
After analysis works, one click promotes it to a scheduled AWS pipeline:
- S3 data lake for storage
- Step Functions for orchestration
- CloudWatch for monitoring and alerting
- Scheduled runs with drift detection
- Pipeline dashboard showing run history

---

## Data sources — v1 scope (do not add more without explicit instruction)

- CSV file upload (drag and drop)
- Excel file upload (.xlsx)
- Public URL (CSV or Excel)

Database connectors, API connections, S3 browser, Power BI connectors —
all deferred to v2. Scope discipline is what makes v1 ship.

---

## Output standard — every analysis must produce ALL of these

- KPI cards: key metrics with delta vs previous period where calculable
- Multi-panel charts: minimum 2, maximum 4, each answering a specific
  question about the data
- Anomaly callouts: flag values that are statistically unusual
- AI insight narrative: 3-5 sentences in plain English explaining what
  the data actually means, written for a non-technical stakeholder
- Conversation continues: "show me by department", "why is this dropping",
  "which handler has the most redos" — each turn refines and rebuilds

---

## UI standard — executive level, non-negotiable

Reference: Retool, Linear, Vercel — professional dark theme, real visual
hierarchy, proper typography (Inter or Geist font).

Required pages:
- Landing page: explains value proposition in 5 seconds, has demo mode
- Analysis workspace: split panel — conversation on left, dashboard on right
- Demo mode: built-in synthetic manufacturing dataset so anyone can try
  immediately without uploading anything

Zero tolerance:
- No NASA branding anywhere (navbar, footer, anywhere)
- No "Built for researchers, by researchers"
- No placeholder text left in production UI
- No basic Tailwind defaults — everything must look intentional

---

## Manufacturing domain — demo data examples

The built-in demo dataset is synthetic manufacturing data covering:
- Defect/redo rates by account and client
- Department-level redo analysis by month
- Equipment and equipment handler redo rates
- Production line performance and quality KPIs

This domain is chosen because the project owner is a manufacturing data
analyst. The demo must feel real, not generic. Use realistic column names,
realistic value ranges, realistic anomalies.

---

## Portfolio requirements — all four roles covered

Every technical decision must demonstrate skills relevant to:
- AI Engineer: RAG pipeline, conversation memory, LLM grounding, prompt
  engineering, evaluation
- Data Scientist: statistical analysis, methodology retrieval, insight
  generation, data profiling
- Data Engineer: AWS Lambda, S3, Step Functions, CloudWatch, pipeline
  orchestration, data quality
- Data Analyst: KPI dashboard, business insight narrative, domain-aware
  analysis, iterative refinement

---

## Current tech stack

- Backend: Python 3.11, FastAPI
- Embeddings: sentence-transformers (all-MiniLM-L6-v2)
- Vector store: ChromaDB (persistent, cosine similarity, HNSW)
- LLM: Anthropic claude-sonnet-4-6 via API
- Execution: AWS Lambda (python:3.11, photon-data-science layer,
  512MB, 30s timeout, subprocess with PYTHONPATH=/opt/python)
- Storage: AWS S3 (photon-analysis-storage, us-east-1)
- Frontend: React + Vite + Tailwind CSS
- Auth: API key middleware (PHOTON_SKIP_AUTH=1 for local dev)

## What is NOT built yet (build in this order)

1. Conversational memory layer (most critical missing piece)
2. Multi-panel KPI dashboard output format
3. AI insight narrative generation (second LLM pass)
4. Excel file upload support
5. Drag-and-drop file upload UI
6. Split-panel workspace UI (conversation left, dashboard right)
7. Demo mode with synthetic manufacturing data
8. Landing page
9. Pillar 2: S3 + Step Functions + CloudWatch pipeline

---

## Non-negotiables — never regress

- No secrets or API keys committed. Ever.
- No in-process exec() for user code. Lambda only.
- No empty stub files.
- No fallback to unsafe execution if Lambda fails — return clear error.
- No NASA branding in the UI.
- Commit after every meaningful change, push immediately.
- Update PROGRESS.md every session.
- Log every non-trivial decision in DECISIONS.md before implementing.
- Explain every change in plain language — project owner must be able to
  defend every decision in any interview without notes.

---

## Workflow — every session

1. Read this file and PROGRESS.md before starting anything
2. Use Claude Sonnet 4.6 HIGH — verify before first code change
3. Before ANY frontend code: read docs/DESIGN.md completely
4. Commit each logical piece separately with Conventional Commits
5. Push after every commit
6. Update PROGRESS.md at session end
7. Explain every decision in plain language as you go

## Reference files

- docs/DESIGN.md — MANDATORY read before any frontend code
- docs/DECISIONS.md — architectural decisions, append-only
- docs/PROGRESS.md — session log, newest entry on top
- photon/app/services/vector_db.py — ChromaDB layer
- photon/app/services/llm.py — Anthropic API generation
- photon/app/services/profiler.py — data profiling
- photon/app/services/lambda_executor.py — AWS Lambda execution
- photon/app/routes/workflow.py — main pipeline route
