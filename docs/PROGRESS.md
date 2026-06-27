# Progress log

Chronological. Newest entry on top. "What happened" lives here.
"Why we decided it" lives in DECISIONS.md.

---

## 2026-06-26 — Session 7 (Phase 3: end-to-end pipeline confirmed working)

**Did:**
- Confirmed full end-to-end pipeline works: question + CSV URL in, executed
  result + chart out, zero errors
- Test: airtravel.csv (12 rows × 4 cols) via public URL
  - Profiler: detected tabular, 4 columns, 0 nulls — correct
  - Playbook retrieval: tabular methodology selected — correct
  - LLM: generated 4-panel matplotlib analysis (trend line, bar chart,
    histogram, summary stats panel)
  - Lambda execution: exit_code 0, no stderr, chart returned as base64 PNG
- Fixed two startup bugs found during testing:
  - Added python-dotenv to requirements.txt; added load_dotenv() at top of
    main.py so .env is loaded automatically on server start
  - Fixed .env.example: ANTHROPIC_KEY → ANTHROPIC_API_KEY (must match
    what llm.py reads via os.environ.get)
  - Added PHOTON_SKIP_AUTH=1 to .env.example with production warning
- Added "Running locally" section to README with correct uvicorn command
  (uvicorn app.main:app --reload --app-dir photon from repo root)

**Key things to know for interviews:**
- The correct uvicorn invocation is `uvicorn app.main:app --reload
  --app-dir photon` from the repo root. --app-dir adds photon/ to
  sys.path so `from app.X import ...` resolves inside the package.
- load_dotenv() must be the very first call in main.py, before any other
  imports, so env vars are set before FastAPI/services read them at import time.
- Lambda can only read data from URLs or data embedded in the code —
  local file paths on the developer's machine don't exist inside the
  AWS Lambda execution environment.

**What's done so far:**
- Phase 0: Security — key rotation, Docker sandbox replacing exec(), 503 guard
- Phase 1: Repo hygiene — node_modules scrubbed, empty stubs deleted, requirements rebuilt
- Phase 2a: ChromaDB — persistent vector store, rebuild_index script, query route
- Phase 2b: Full pipeline — profiler → playbook retrieval → LLM generation → workflow route
- Phase 3: Lambda execution — sandbox confirmed, wired into execute + workflow routes
- Phase 3 verified: end-to-end test passed, exit_code 0, chart returned

**What's NOT built yet:**
- Frontend data upload UI: replace hardcoded NASA dataset selector with
  "bring your own data" — file upload or URL input
- Automated end-to-end integration test suite
- Pillar 2 (AWS pipeline promotion): not started

**Next session:**
Build the frontend upload UI so a user can drop a CSV URL and ask a
question from the browser, triggering the full pipeline and seeing the
executed result and chart without touching the terminal.

---

## 2026-06-23 — Session 6 (Phase 3: Lambda execution wired into pipeline)

**Did:**
- Confirmed Lambda sandbox works: pandas/numpy/matplotlib import, charts
  save to /tmp/output.png and return as base64, exit code 0
- Created photon/app/services/lambda_executor.py: execute_via_lambda(code)
  Calls photon-code-executor via boto3 RequestResponse invocation
  Handles FunctionError (Lambda-side crash) and returns consistent dict
- Rewrote photon/app/routes/execute.py: removed all Docker/subprocess logic,
  now calls execute_via_lambda(). Response shape unchanged (images[] list).
  Updated _SAVEFIG_SNIPPET path from /workspace/ to /tmp/ (Lambda writable dir)
- Updated photon/app/routes/workflow.py: added step 5 (execute_via_lambda)
  Full pipeline now: load → profile → retrieve → generate → execute
  Response now includes "execution" key with stdout/stderr/exit_code/output_image
- Added boto3 to requirements.txt
- Updated .env.example with AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION
- Added IAM least-privilege setup instructions to aws/README.md
  Policy: lambda:InvokeFunction on photon-code-executor ARN only

**Key things to know for interviews:**
- The /workflow/generate endpoint now returns real executed results, not just
  generated code. One HTTP call goes from question+data to actual output.
- Lambda FunctionError vs user code failure: FunctionError means the Lambda
  handler itself crashed (timeout, OOM, import error in the handler). A
  non-zero exit_code in the body means user code failed. These are different
  failure modes and handled separately.
- timed_out is always False in the execute route because Lambda enforces its
  own timeout at the infrastructure level — we never see a partial execution.
- Least-privilege IAM: backend credentials can ONLY invoke one specific Lambda
  function. A leaked key cannot touch S3, IAM, other functions, or anything else.
- boto3 picks up credentials from environment variables automatically:
  AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION.

**What's done so far:**
- Phase 0: Security — key rotation, Docker sandbox replacing exec(), 503 guard
- Phase 1: Repo hygiene — node_modules scrubbed, empty stubs deleted, requirements rebuilt
- Phase 2a: ChromaDB — persistent vector store, rebuild_index script, query route
- Phase 2b: Full pipeline — profiler → playbook retrieval → LLM generation → workflow route
- Phase 3: Lambda execution — sandbox confirmed, wired into execute + workflow routes

**What's NOT built yet:**
- Frontend data upload UI: replace hardcoded NASA dataset selector with
  "bring your own data" — file upload or URL input
- End-to-end integration test: real CSV → profile → playbook → LLM → Lambda → check results
- Pillar 2 (AWS pipeline promotion): not started

**Next session:**
Build the frontend upload UI so a user can drop a CSV and ask a question
from the browser, triggering the full pipeline and seeing real results.

---

## 2026-06-23 — Session 5 (Phase 2b: profiler + playbooks + LLM + workflow)

**Did:**
- Built data profiler (profiler.py): load_dataframe() + profile()
  Detects: tabular / time_series / wide_format
  Returns: row_count, column_count, per-column types/nulls, summary sentence
  4 tests: tabular detection, time_series detection, null detection, CSV load
- Built methodology playbooks (data/playbooks/): tabular.md, time_series.md,
  wide_format.md — real actionable content, not placeholder text
- Added add_playbook() and search_playbooks() to vector_db.py
  Playbooks live in a separate photon_playbooks collection
  Retrieval is a metadata filter (where data_type=X), not similarity search
- Built load_playbooks.py script to ingest all three playbooks into ChromaDB
- Built LLM generation layer (llm.py): generate_analysis_code()
  Calls claude-sonnet-4-6 with structured 4-section prompt
  Strips accidental markdown fences from response
  Raises ValueError with clear message if ANTHROPIC_API_KEY not set
  3 tests: returns code, strips fences, raises on missing key
- Wired workflow route (routes/workflow.py) to the full pipeline:
  load_dataframe → profile → search_playbooks → generate_analysis_code
  New request shape: {question, source}
  New response shape: {code, profile, methodology_used}
  Old Jinja2/notebook approach completely replaced
- Removed Jinja2 and nbformat from requirements.txt (no longer used)
- Added pandas and anthropic to requirements.txt
- Created .env.example with ANTHROPIC_API_KEY format

**Key things to know for interviews:**
- The profiler runs before the LLM — the LLM sees real column names and types,
  not guesses from a filename. This is why the generated code works on first run.
- Playbook retrieval is a metadata filter, not similarity search. The profiler
  gives an exact classification; we don't need fuzzy matching.
- Two ChromaDB collections: photon_datasets (34 NASA datasets, similarity search)
  and photon_playbooks (3 methodology guides, metadata filter). Separate
  collections because mixing them would contaminate both retrieval paths.
- The workflow route returns code but does NOT execute it. Execution is a
  separate step — the caller hits /execute with the returned code. This keeps
  the concerns cleanly separated and lets the user inspect the code before running.
- Mocking in tests: we mock the Anthropic client because real API calls cost
  money, require a secret in CI, and are non-deterministic. The tests verify
  our code's logic — key reading, prompt building, fence stripping — not Anthropic's.

**What's done so far:**
- Phase 0: Security — key rotation, Docker sandbox replacing exec(), 503 guard
- Phase 1: Repo hygiene — node_modules scrubbed, empty stubs deleted, requirements rebuilt
- Phase 2a: ChromaDB — persistent vector store, rebuild_index script, query route
- Phase 2b: Full pipeline — profiler → playbook retrieval → LLM generation → workflow route

**What's NOT built yet (Phase 3 — next):**
- Connect workflow to execute: POST /workflow/generate → code → POST /execute → results
  The two endpoints exist. They just haven't been wired into a single flow yet.
- Frontend data upload UI: replace hardcoded NASA dataset selector with
  "bring your own data" — file upload or URL input
- End-to-end integration test: real CSV → profile → playbook → LLM → execute → check results
- Pillar 2 (AWS): not started, not started until Pillar 1 is interview-ready

**Next session task — Phase 3:**
Connect the two endpoints. The workflow route returns code. The execute endpoint
runs code. Build a thin integration layer (or update the frontend) so a user
can go from "question + file" to "real executed results" in one action.
Then build the frontend upload UI.

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
