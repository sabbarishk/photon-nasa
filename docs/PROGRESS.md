# Progress log


Chronological. One entry per work session, newest entry on top. This is the
"what happened and when" record — rationale for *why* belongs in DECISIONS.md,
not here.

---

## 2026-06-21 — Session 5: Phase 2a — ChromaDB vector store

**Did:**

**ADR-006 written first** — documented why ChromaDB over Pinecone (no API key,
runs locally), Weaviate (over-complex schema system for this stage), FAISS
(no metadata, no persistence layer, pushes hard problems back onto app code),
and the optimised flat JSON approach (performance ceiling, weak interview
story). Decision is in docs/DECISIONS.md.

**`photon/app/services/vector_db.py` — new, clean ChromaDB service**
- `PersistentClient(path=data/chroma/)` with `hnsw:space: cosine` so
  distances are in [0, 2] and `1.0 - distance` gives cosine similarity [0, 1].
- `add_dataset(dataset)`: embeds title + summary via `hf_api.get_embedding`,
  then `upsert`s (idempotent) into the collection with format/tags/source_url
  as metadata.
- `search(query, top_k)`: embeds query, guards against `n_results > count()`
  (ChromaDB 1.x raises on this), returns `{"id", "score", "meta"}` list
  matching the existing API contract.
- `count()`: returns collection size.
- `_reset(persist_dir)`: resets singletons + deletes the collection (needed
  because EphemeralClient is a process-level singleton in ChromaDB 1.x).
- `:memory:` support via `EphemeralClient` when `CHROMA_PERSIST_DIR=:memory:`.
- `data/chroma/` added to `.gitignore`.

**`photon/scripts/rebuild_index.py` — one-time ingestion from vectors.json**
- Reads the flat JSON source of truth, calls `add_dataset` for each entry.
- Confirmed: `34 datasets indexed` on first run.
- Runnable as: `PYTHONPATH=photon python -m photon.scripts.rebuild_index`

**`photon/app/routes/query.py` — migrated to ChromaDB**
- Replaced `VectorStore("data/vectors.json")` + manual embedding call with a
  single `vector_db.search(req.query, req.top_k)` call.
- API contract unchanged — frontend has no idea anything changed.

**`photon/app/services/vector_store.py` — deprecated**
- Added deprecation comment at top. File retained for reference during Phase
  2a verification; will be deleted once ChromaDB path is confirmed stable.

**Tests: `photon/tests/test_vector_db.py`**
- `test_add_and_search`: adds 3 datasets with mocked orthogonal embeddings,
  searches for one by meaning, asserts correct ordering and score > 0.9.
- `test_count`: asserts count() == 0 before adds, 1/2 after each, and still
  2 after an upsert of an existing id (idempotency check).
- All 6 tests pass (including pre-existing ones).

**Non-obvious fixes discovered during this session:**
- ChromaDB 1.x `EphemeralClient` is a process-level singleton: calling it
  twice returns the same in-memory store. `_reset()` must delete the
  collection (not just clear the Python reference) to isolate tests.
- ChromaDB raises if `n_results > count()`: search() now guards with
  `min(top_k, coll.count())`.
- Windows file locking: `PersistentClient` memory-maps HNSW files; temp dirs
  can't be deleted while the client is alive. Solved by using `EphemeralClient`
  (`:memory:`) in tests instead of temp directories.

**Commits pushed:**
- `feat: add ChromaDB vector store with persistent index`
- `test: add vector_db tests for ChromaDB add/search and count`
- `docs: update PROGRESS.md for session 5`

**Next session options (pick one):**
- **Phase 2b: Hash API keys at rest.** `auth.py` still compares keys in
  plaintext. Replace with bcrypt/SHA-256 + `secrets.compare_digest`. This is
  the last outstanding Phase 0 security item.
- **Phase 2b: Test coverage for high-risk routes.** Write integration tests
  for `/query` (with the new ChromaDB backend), `/workflow/generate`, and
  the `/execute` Docker sandbox path (requires Docker running).
- **Phase 2b: Delete `vector_store.py`** (now fully superseded by vector_db.py),
  confirm no remaining imports, clean up `test_vector_store.py`.

---

## 2026-06-21 — Session 4: Phase 1 repo cleanup (4 items)

**Did:**

**Item 1 — node_modules removed from git history**
- `git rm --cached -r frontend/node_modules/` untracked 2,432 files.
- Added `node_modules/` to `.gitignore`.
- `git filter-repo --path frontend/node_modules --invert-paths` rewrote
  all history to remove the blobs from the one commit that added them.
- Repo pack size: **11.48 MiB → 1.03 MiB** (11× reduction). Zero history
  references to node_modules remain.
- Force-pushed the rewritten history.

**Item 2 — Duplicate frontend deleted**
- Compared `frontend/` (root) vs `photon/frontend/`:
  - `frontend/`: Vite 5, React 18, JSX, real components (Navbar, Hero,
    Search, WorkflowGenerator, Footer), DatasetContext, api.js service
    wired to all 4 backend endpoints. The real application.
  - `photon/frontend/`: create-react-app scaffold (officially deprecated
    by Meta in 2023), untouched default boilerplate ("Edit src/App.js
    and save to reload"), `cra-template` listed as a runtime dependency.
    Never developed.
- Deleted `photon/frontend/` entirely (17 tracked files + local
  node_modules on disk).
- Removed stale `timeout` parameter from `executeNotebook()` in
  `frontend/src/services/api.js` and its callsite in
  `WorkflowGenerator.jsx` — the backend no longer accepts it (server
  enforces 15s constant via Docker, per ADR-005).

**Item 3 — Empty stub files deleted**
- Confirmed `photon/app/services/llm.py`, `embedding.py`, `vector_db.py`
  were exactly 0 bytes. Nothing imports them. Deleted via `git rm`.
- `photon/requirements.txt` had 3,056 bytes of content — not empty,
  handled in Item 4.

**Item 4 — requirements.txt rebuilt from scratch**
- Old file was UTF-16 LE (every char followed by a null byte) and was a
  full `pip freeze` of the entire virtualenv — including torch,
  weaviate-client, Cartopy, grpcio, scikit-learn, sympy, etc. that are
  never imported by any server file.
- Audited every `import` in `photon/app/` and `photon/scripts/`. Rebuilt
  `requirements.txt` as UTF-8, Unix line endings, listing only:
  `fastapi`, `uvicorn[standard]`, `starlette`, `pydantic`, `Jinja2`,
  `nbformat`, `requests`, `sentence-transformers`, `numpy`, `redis`,
  `chromadb` (last two optional — app falls back gracefully if absent).
- Created `photon/requirements-dev.txt`: `pytest`, `httpx`,
  `pytest-asyncio`, `ruff`.

**Status:** All four Phase 1 cleanup items complete. Repo is now in a
clean state: single frontend, no empty stubs, no committed dependency
trees, correct requirements encoding.

**Next session options (pick one):**
- Phase 2: Improve test coverage — the existing 2 tests cover none of
  the high-risk endpoints. Write integration tests for `/execute`,
  `/query`, and `/workflow`.
- Phase 2: Resolve ADR-002 (architecture scope) and begin the RAG
  pipeline upgrade — replace static Jinja2 templates with actual
  LLM-grounded code generation.

---

## 2026-06-21 — Session 3: Phase 0 security fix — Docker sandbox replaces exec() RCE

**Did:**
- Wrote ADR-005 documenting the exec() RCE, all four sandboxing options
  considered, and why local Docker was chosen over cloud sandboxes and
  restricted subprocess approaches.
- Created `docker/sandbox/Dockerfile`: minimal `python:3.11-slim` image with
  pandas, numpy, matplotlib, running as non-root user `sandbox`.
- Rewrote `photon/app/routes/execute.py` from scratch. exec() is gone
  entirely — no fallback, no commented-out version. Replaced with:
  - `docker run --rm --network none --memory 256m --cpus 0.5` per request
  - UUID-named containers so timed-out containers can be killed by name
  - `subprocess.run(..., timeout=15)` enforcing a hard 15s wall-clock limit;
    `docker kill <name>` called in the timeout handler to stop the container
  - HTTP 503 with a clear message if Docker is not running — no silent fallback
  - Removed the caller-controlled `timeout` parameter (was cosmetic; now a
    server-side constant)
  - Removed the `/test-imports` debug endpoint (imported from server process,
    not the sandbox — meaningless and leaks server environment info)

**How to use the new endpoint:**
1. Build the sandbox image once: `docker build -t photon-sandbox docker/sandbox/`
2. Ensure Docker Desktop (or the Docker daemon) is running.
3. POST to `/execute/notebook` with `{"code": "..."}` — no API change beyond
   the removed `timeout` field.

**Remaining Phase 0 security items:**
- `auth.py` stores and compares keys in plaintext JSON — should be hashed at
  rest. Deferred; lower severity than the now-fixed RCE.

**Note for interviews:** "The original endpoint ran user-submitted Python code
via exec() in the server process — a textbook RCE with no isolation, no
resource limits, and a timeout field that was accepted but never enforced. I
replaced it with Docker container isolation: no network, 256 MB RAM cap, 0.5
CPU cap, hard 15-second kill enforced by killing the container by name. The
server returns 503 if Docker isn't running rather than silently falling back
to the unsafe path. I documented the four alternatives I considered in ADR-005
before writing a line of code."

---

## 2026-06-21 — Session 2: Phase 0 security fix — leaked API key rotation and history scrub

**Did:**
- Rotated the leaked API key. Old key (`h9Yf4aL8eITjxqeWPBvXyd3laRJB3eDu`)
  was committed in plaintext in `photon/data/api_keys.json`. Generated a new
  key using `scripts/create_api_key.py`, removed the old entry from the file.
- Untracked `photon/data/api_keys.json` from git with `git rm --cached`. Added
  an explicit entry to `.gitignore` so future keys cannot be accidentally
  committed.
- Scrubbed the old key from the entire git history using `git filter-repo
  --path photon/data/api_keys.json --invert-paths`. All 34 commits were
  rewritten; `git log --all -- photon/data/api_keys.json` now returns empty.
- Force-pushed the rewritten history to GitHub origin.

**Why git filter-repo over the alternatives:** see ADR-004.

**Remaining Phase 0 security items (not yet fixed):**
- `/execute` endpoint still runs submitted code via in-process `exec()` — full
  RCE risk, no sandboxing, timeout not enforced. This is the next priority.
- `auth.py` stores and compares keys in plaintext JSON — should be hashed at
  rest (e.g. `secrets.compare_digest` + bcrypt or SHA-256). Deferred until
  after the execute endpoint is fixed, since that's the higher-severity issue.

**Note for interviews:** "I found an API key committed to a public repo,
rotated it immediately, used git filter-repo to scrub all history, and
force-pushed. I also .gitignore-d the file and added a comment to explain
why, so the pattern is clear to any future contributor."

**Next session:** Phase 0 continues — sandbox the `/execute` endpoint (the
RCE finding). This requires a real design decision: container-based isolation
(Docker) vs. a restrictedd subprocess approach vs. removing the endpoint
entirely until sandboxing is production-ready.

---

## 2026-06-21 — Session 1: Audit and direction-setting (no code changes yet)

**Did:**
- Full audit of the existing `photon-nasa` repository (backend, frontend,
  tests, CI, docs).
- Set up the project memory system: `CLAUDE.md`, `docs/DECISIONS.md`, this
  file.

**Found (full detail in the audit, summarized here):**
- A live-looking API key committed to the public repo
  (`photon/data/api_keys.json`) — needs rotation and git history scrub.
- `/execute` endpoint runs submitted code via in-process `exec()` with zero
  sandboxing — full remote code execution risk. The `timeout` field on the
  request is accepted but never enforced.
- The project is not actually a RAG pipeline yet — it's semantic search +
  static Jinja2 templates. `llm.py`, `embedding.py`, `vector_db.py` are empty
  stub files; no LLM generation step exists.
- Repo hygiene: two duplicate frontend directories, `node_modules` committed to
  git (~49MB, 2432 files), `requirements.txt` saved as UTF-16 with no dev/prod
  split, `redis` and `chromadb` imported in code but absent from
  `requirements.txt` (dead code paths), scattered test/data files outside
  `tests/`.
- Testing: 2 trivial tests total, none covering the highest-risk endpoint
  (`execute.py`).

**Discussed:**
- Generalizing beyond NASA-only scope into a two-pillar system (RAG discovery +
  AWS productionization) — validated this is a real, recognized gap in the
  industry (notebook-to-production handoff), not a reinvented wheel.
- Reframed the actual goal: this project needs to be interview-ready for
  AI Engineer / Data Engineer / Data Scientist / Data Analyst applications —
  not optimized for GitHub stars.
- Scope/sequencing trade-offs (build both pillars in parallel vs. sequence
  Pillar 1 to a polished state first), AWS cost realism (avoid MWAA, prefer
  serverless), and documentation workflow.

**Status:** Architecture direction (ADR-002) is proposed, not yet finalized.
No code has been changed yet. Security findings are documented but not fixed
yet.

**Next session:** Resolve ADR-002 (confirm scope/sequencing), then start
Phase 0 — security fixes (rotate leaked key, scrub git history, sandbox the
execute endpoint, enforce the timeout).
