# Architecture decisions log

Append-only. Each entry is numbered and dated. Once written, not edited —
if a decision changes, add a new ADR that supersedes it and reference it.
Status: Proposed / Accepted / Superseded.

This file exists for one reason: when an interviewer asks "why did you build
it that way," the honest answer — including what you rejected and why — is
already written down, not reconstructed from memory under pressure.

---

## ADR-001 — Security hardening before any feature work

**Date:** 2026-06-21
**Status:** Accepted — completed

**Context:** Initial audit found three critical issues in the public repo:
(1) a plaintext API key committed to git in photon/data/api_keys.json,
(2) the /execute endpoint running arbitrary user code via in-process exec()
with full access to the server's filesystem, network, and environment,
(3) a timeout parameter accepted by the API but never enforced anywhere.

**Decision:** Fix all three before any new feature work. Security first.

**Alternatives considered:** Defer until after the architecture pivot.
Rejected — the repo was public and the key was live. "I found and fixed an
RCE before building further" is a stronger interview story than leaving a
known critical vulnerability open.

**What was done:**
- Rotated the exposed API key (treated as permanently compromised regardless
  of the git scrub, because GitHub caches objects for up to 90 days)
- Scrubbed api_keys.json from all 34 commits using git filter-repo
- Replaced in-process exec() with Docker container isolation:
  python:3.11-slim base, --network none, 256MB RAM, 0.5 CPU, 15s wall-clock
  timeout enforced by subprocess.run + docker kill, --rm auto-cleanup
- Added 503 guard: if Docker is unavailable, return a clear error — never
  fall back to unsafe execution
- Added .env to .gitignore, added .env.example as the pattern

---

## ADR-002 — What Photon actually is (final direction)

**Date:** 2026-06-22
**Status:** Accepted — supersedes the Proposed version from 2026-06-21

**Context:** Three directions were considered and rejected before landing here:

1. Stay NASA-specific and publish as a research paper — rejected. A paper
   doesn't demonstrate shipped engineering. NASA's own portal already does
   natural language dataset search, as confirmed by a NASA data science lead
   who reviewed the original project.

2. Multi-source dataset search + code generation — rejected. ChatGPT,
   Julius AI, and a dozen others generate code from a dataset description.
   "Describe a dataset and get pandas code" is a solved problem. A hiring
   manager would see through it in 60 seconds.

3. RAG over analysis methodology documentation — rejected. A searchable
   library of "how to analyze climate data" articles is just documentation
   with a search bar. It doesn't solve a pain that practitioners actually feel.

**The actual gap nobody has filled:**
Every LLM tool generates code. None of them run it. The user still has to
copy the generated code, paste it somewhere, run it, debug it, and decide
whether to trust it. The generation and the execution are always separate.

**Decision:** Photon bridges that gap. It is an AI analysis assistant that
writes analysis code AND runs it against real data AND returns real results —
not hallucinated output, but numbers from actual execution. The Docker sandbox
is not a security feature. It is the core product differentiator.

The RAG layer makes the generated code methodologically appropriate, not just
syntactically correct. The vector store holds analysis playbooks for different
data types. The data profiler detects what kind of data the user has and
retrieves the right methodology before the LLM writes a single line of code.

**Why this can't be replicated in ChatGPT:**
You cannot paste your data, get code written, have that code run against your
real data, and get real numbers back — all in one shot, in a repeatable,
open-source, self-hostable workflow. ChatGPT generates. Photon executes.

**Two-pillar architecture, built in sequence:**
- Pillar 1: Profile → Retrieve methodology (RAG) → Generate → Execute →
  Return real results. Build this first, to a polished and deeply understood
  state.
- Pillar 2: Promote a working analysis to a scheduled AWS pipeline with
  monitoring and data quality checks. Start only after Pillar 1 is solid.

**Interview answer for all four target roles:**
- AI Engineer: "I built a RAG system where retrieval is triggered by automatic
  data profiling, and I built an execution layer so LLM output is verified
  against real data before it reaches the user."
- Data Engineer: "The pipeline promotion layer scaffolds production AWS
  infrastructure around a validated analysis — S3, Lambda, CloudWatch."
- Data Scientist: "The methodology retrieval means the analysis approach is
  appropriate for the data type before the LLM writes any code."
- Data Analyst: "You describe what you want to know. You get the actual answer
  from your actual data, with the code visible so you can verify it."

---

## ADR-003 — Project memory and documentation workflow

**Date:** 2026-06-21
**Status:** Accepted

**Context:** Project owner is building this hands-on via Claude Code while
learning, and needs to be able to defend every decision in interviews without
re-explaining context at the start of every session.

**Decision:** Three-file documentation system:
- CLAUDE.md: stable rules and facts, auto-loaded every Claude Code session
- docs/DECISIONS.md: durable rationale, append-only, interview prep material
- docs/PROGRESS.md: chronological session log, newest entry on top

**Alternatives considered:** Single README-as-memory file. Rejected — mixing
stable rules with a constantly-changing plan makes both unreliable.

---

## ADR-004 — ChromaDB as the vector store

**Date:** 2026-06-22
**Status:** Accepted — completed

**Context:** The original vector store was a flat JSON file with NumPy cosine
similarity. Fine for 34 rows. Wrong answer for anything beyond that, and a
weak interview answer compared to a real vector database.

**Decision:** ChromaDB, running locally with persistent storage.

**Why ChromaDB over alternatives:**
- Pinecone: managed cloud service, requires an account and API key. Anyone
  cloning the repo can't run it without signing up. Wrong for open source.
- Weaviate: full server process with Docker Compose required just to run the
  db. Adds operational overhead before you've written a single line of app code.
- FAISS: Meta's library, fast, but no built-in persistence, no metadata
  filtering, and the API doesn't map to what Pinecone/Weaviate/Qdrant expose.
  Harder to explain the upgrade path.
- ChromaDB: pip install, zero accounts, runs in-process, persistent by default,
  HNSW under the hood (O(log n) vs flat scan's O(n)), and the API maps
  directly to every other production vector database. Knowing ChromaDB makes
  explaining Pinecone or Weaviate in an interview straightforward.

**Key implementation decisions:**
- hnsw:space: cosine — without this, ChromaDB defaults to L2 distance, which
  gives wrong results for text embeddings that aren't L2-normalized
- upsert not add — rebuild_index.py can run multiple times safely
- min(top_k, count()) guard — ChromaDB 1.x raises if you request more results
  than exist in the collection
- EphemeralClient for tests — persistent client memory-maps HNSW files;
  Windows can't delete temp directories while maps are open. In-memory client
  has no files, no lock, no test isolation problem.

---

## ADR-005 — Repo cleanup decisions

**Date:** 2026-06-22
**Status:** Accepted — completed

**Context:** Initial audit found several repo hygiene issues that would
immediately signal "not production-aware" to a hiring manager reviewing the
repo.

**Decisions made and why:**
- node_modules removed from git: generated output, belongs in .gitignore,
  never in source control. Scrubbed with git filter-repo.
- Duplicate frontend removed: two frontends coexisted — a real Vite/React
  app (frontend/) and an untouched create-react-app scaffold (photon/frontend/)
  that was never developed past npx create-react-app output. CRA was deprecated
  by Meta in 2023. Kept frontend/, deleted photon/frontend/.
- Empty stub files deleted: llm.py, embedding.py, vector_db.py were 0 bytes.
  They import without error but do nothing. Misleads anyone reading the code.
  Deleted. Will be created properly when actually implemented.
- requirements.txt rebuilt: was UTF-16 LE encoded (PowerShell artifact), was
  a full pip freeze of the entire virtualenv including PyTorch, Cartopy,
  weaviate — packages the server never imports. Rebuilt as UTF-8, 11 packages
  the server actually uses. requirements-dev.txt created separately for
  pytest, ruff, httpx so production installs don't pull in test tooling.
- Stale timeout parameter removed from frontend API call: frontend/src/
  services/api.js was still passing a timeout field to the execute endpoint
  that was removed from the backend in Phase 0.
