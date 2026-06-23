# Progress log

Chronological. Newest entry on top. "What happened" lives here.
"Why we decided it" lives in DECISIONS.md.

---

## 2026-06-22 — Session 4 (direction locked, all docs updated)

**Did:**
- Locked final product direction after rejecting three earlier ideas
  (see ADR-002 for full reasoning and what was rejected)
- Rewrote all three memory files to reflect final direction:
  CLAUDE.md, docs/DECISIONS.md, docs/PROGRESS.md

**What Photon is now (locked):**
AI analysis assistant. Describe what you want to know about your data.
Photon profiles it, retrieves the right analysis methodology via RAG,
generates code grounded in that methodology, runs it in Docker, and
returns real results — not hallucinated output. Any data: CSV upload,
URL, or built-in NASA examples.

**What's done so far:**
- Phase 0: Security — key rotation + git history scrub, Docker sandbox
  replacing exec(), 503 guard if Docker unavailable
- Phase 1: Repo hygiene — node_modules scrubbed, duplicate frontend
  removed, empty stubs deleted, requirements.txt rebuilt clean
- Phase 2a: ChromaDB — real vector store replacing flat JSON, rebuild_index
  script, query route migrated, tests written

**What's NOT built yet (Phase 2b — next):**
- Data profiler: automatic schema detection, type inference, null analysis,
  data type classification (tabular / time series / geospatial / etc)
- Methodology playbook knowledge base: curated analysis guides loaded into
  ChromaDB, covering common data types the profiler can detect
- LLM generation layer: llm.py calling Anthropic API, grounded in retrieved
  methodology + profiled schema
- Workflow route: wired to profiler → retrieval → LLM → execute pipeline
- Frontend data upload UI: replace hardcoded NASA dataset selector with
  "bring your own data" upload
- Pillar 2 (AWS): not started, not started until Pillar 1 is solid

**Next session task — Phase 2b:**
Build the data profiler first. This is the entry point to everything.
Without profiling, there's nothing to retrieve methodology for.
Profile output feeds ChromaDB retrieval query AND the LLM prompt context.

---

## 2026-06-22 — Session 3 (Phase 2a: ChromaDB)

**Did:**
- Replaced flat JSON vector store with ChromaDB (persistent, HNSW, cosine)
- Built vector_db.py: add_dataset(), search(), count() methods
- Built rebuild_index.py: ingests existing vectors.json into ChromaDB
- Migrated query.py route to use vector_db.py — API contract unchanged
- Kept vector_store.py with DEPRECATED comment (remove after verification)
- Wrote two tests: test_add_and_search, test_count using EphemeralClient
- Fixed commit attribution — all commits now under sabbarishk only

**Key things to know for interviews:**
- HNSW = O(log n) vs flat scan's O(n) — the scalability argument
- hnsw:space: cosine matters — L2 default gives wrong results for text
- EphemeralClient for tests because Windows locks HNSW memory-mapped files
- EphemeralClient is a process-level singleton — must delete collection
  between tests, not just create a new client

---

## 2026-06-22 — Session 2 (Phase 1: repo cleanup)

**Did:**
- Removed node_modules from git history (git filter-repo, 11MB → 1MB)
- Deleted photon/frontend/ (abandoned CRA scaffold, never developed)
- Deleted empty stub files: llm.py, embedding.py, vector_db.py
- Rebuilt requirements.txt (UTF-8, 11 real packages, not 83-package freeze)
- Created requirements-dev.txt (pytest, ruff, httpx, pytest-asyncio)
- Removed stale timeout arg from frontend/src/services/api.js

---

## 2026-06-21 — Session 1 (Phase 0: security + project memory setup)

**Did:**
- Full audit of original photon-nasa repository
- Set up CLAUDE.md, docs/DECISIONS.md, docs/PROGRESS.md
- Rotated leaked API key (photon/data/api_keys.json — was public)
- Scrubbed api_keys.json from all git history with git filter-repo
- Replaced in-process exec() in execute.py with Docker container sandbox:
  python:3.11-slim, --network none, 256MB, 0.5 CPU, 15s timeout,
  subprocess.run + docker kill, --rm cleanup, 503 if Docker unavailable
- Created docker/sandbox/Dockerfile

**Key things to know for interviews:**
- Why git rm --cached isn't enough: history still contains the blob
- GitHub retains unreferenced objects for ~90 days — rotate first, scrub
  second. The rotation matters more than the scrub.
- exec() RCE: same process = same filesystem, env vars, network access
- --network none: container cannot make outbound connections
- Timeout enforced by Docker, not by trusting the code to stop
