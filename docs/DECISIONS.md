# Architecture decisions log

Append-only. Each entry is numbered and dated, and once written, is not edited —
if a decision changes, add a new ADR that supersedes it and say so. Status is one
of: Proposed, Accepted, Superseded.

This file exists for one reason: when someone asks "why did you build it that
way," the honest answer — including the options you rejected — should already be
written down, not reconstructed from memory under interview pressure.

---

## ADR-006 — Replace flat JSON vector store with ChromaDB

**Date:** 2026-06-21
**Status:** Accepted

**Context:** The original vector store is a flat JSON file (`data/vectors.json`)
with a hand-written NumPy cosine similarity search. Every query reads the full
file into memory, stacks all embeddings into a NumPy matrix, and brute-forces
the similarity computation. This is fine for 10 documents. At a few thousand
documents it becomes a noticeable bottleneck; at tens of thousands it becomes
untenable. There is also no metadata filtering, no persistence guarantees, and
no standard query interface that a hiring manager would recognise.

The existing `vector_store.py` had ChromaDB hooks stubbed in, but the code used
the old `duckdb+parquet` settings API (removed in ChromaDB 0.4) and contained
incorrect error handling and an import structure that made it untestable. It
was not a real implementation.

**Options considered:**

1. **Keep the flat JSON file, optimise it.** Add better caching, use memory-
   mapped files, tune the NumPy operations. Rejected. The performance ceiling is
   inherent to brute-force linear scan; optimising it just delays the problem.
   More importantly, "I used a flat JSON file with NumPy" is a much weaker
   interview answer than "I used a real vector database."

2. **Pinecone (managed cloud).** Production-grade, serverless, no infrastructure.
   Rejected for the same reason paid cloud sandboxes were rejected in ADR-005:
   requires a signup, an API key, and a billing account. An interviewer cannot
   run the project locally. Adds a hard external dependency and a cost line item.

3. **Weaviate.** Open-source, can run locally via Docker. Full-featured: native
   BM25 hybrid search, multi-tenancy, module system. Rejected as over-complex for
   this stage — the module system and schema definitions add significant
   boilerplate, and Weaviate's primary strength (hybrid search) is not something
   this project needs yet.

4. **FAISS (Facebook AI Similarity Search).** Fast, mature, battle-tested at
   Meta. Pure similarity search — no metadata storage, no persistence layer, no
   query interface. Requires writing the metadata store separately, rebuilding
   the index at startup, and hand-managing persistence. Rejected because it
   pushes all the hard problems (persistence, metadata, filtering) back onto
   application code, giving us less to show an interviewer than ChromaDB does.

5. **ChromaDB (local, persistent).** Open-source vector database with a simple
   Python API, HNSW indexing, cosine/L2/IP distance support, per-document
   metadata storage, metadata filtering, and persistent on-disk storage with no
   external service required. Runs entirely in-process. `pip install chromadb`
   is the only setup step. **Chosen.**

**What ChromaDB gives us over the flat JSON store:**

- **Persistent index:** ChromaDB writes to disk automatically. After the initial
  `rebuild_index` run, the server does not re-embed or re-scan the JSON file
  on startup — it opens the existing index. This is the difference between a
  query being served from a pre-built ANN index (fast) versus a full matrix scan
  (scales linearly with corpus size).
- **HNSW indexing:** Hierarchical Navigable Small World graphs provide
  approximate nearest-neighbour search in `O(log n)` instead of `O(n)`. For
  the current 10-dataset corpus this makes no measurable difference; for 100,000
  datasets it means sub-millisecond query time vs. seconds.
- **Metadata storage and filtering:** Each document can carry arbitrary metadata
  (format, tags, source_url) stored alongside the embedding. Future queries can
  add a `where={"format": "NetCDF"}` clause to pre-filter before ANN search.
  The flat JSON store had no filtering primitive at all.
- **Upsert semantics:** `collection.upsert()` is idempotent. Re-running
  `rebuild_index` updates existing entries rather than duplicating them.
- **Standard interface:** `collection.query(query_embeddings=..., n_results=...)
  is a recognisable, industry-standard interface. It maps directly to what
  Pinecone, Weaviate, and Qdrant all expose. Knowing ChromaDB makes explaining
  those services straightforward in an interview.

**Why local ChromaDB and not a managed service:**
Same reasoning as ADR-005 for Docker vs. paid cloud sandboxes. A portfolio
project must be reproducible on an interviewer's laptop with zero accounts or API
keys. ChromaDB satisfies this requirement while demonstrating genuine vector
database knowledge. The upgrade path to Pinecone or Weaviate Cloud is a one-line
client swap once the project has a deployment budget.

**What we are keeping from the old design:**
- `vectors.json` remains the authoritative source of raw dataset metadata and
  pre-computed embeddings. `rebuild_index.py` reads it to populate ChromaDB.
  If the ChromaDB index is ever deleted, the JSON file is the recovery source.
- `vector_store.py` is deprecated but not deleted immediately — it stays with a
  deprecation notice until Phase 2a is fully verified.

**Consequences:**
- New dependency: `chromadb` (promoted from "optional" to required in
  `requirements.txt`). ChromaDB has native C++ bindings on some platforms;
  `pip install chromadb` may need a few minutes on a clean environment.
- The `data/chroma/` directory is created on first run and must be excluded from
  git (large binary files). Added to `.gitignore`.
- One-time setup step: `python -m photon.scripts.rebuild_index` must be run
  after install to populate the index from `vectors.json`.
- Query response format is unchanged — `{"id": ..., "score": ..., "meta": ...}`.
  Score is converted from ChromaDB cosine distance (`1 - cosine_similarity`) back
  to cosine similarity by computing `1.0 - distance`, preserving the 0–1 range
  the frontend expects.

---

## ADR-005 — Docker container isolation for the /execute endpoint

**Date:** 2026-06-21
**Status:** Accepted

**Context:** The `/execute` endpoint accepted arbitrary user-submitted Python
code and ran it via `exec()` inside the server process. This is a textbook
Remote Code Execution (RCE) vulnerability: submitted code inherits the full
privileges of the server process, has access to the filesystem, can make
network calls, can import any installed package, can exhaust memory or CPU,
and runs forever if it loops. The `timeout` field on the request model was
cosmetic — it was accepted by the API but never actually enforced anywhere.

**Why `exec()` is an RCE, not just a bug:**
`exec()` does not sandbox, parse, or restrict Python code in any way. It runs
code as if you typed it yourself in the Python REPL of the running server
process. An attacker who can call `/execute` can read secret files, delete
data, establish reverse shells, and exhaust every resource on the host — all
with zero extra permissions needed, because the server process is already
running. The only way to fix this is process isolation.

**Options considered:**

1. **Continue using `exec()`, add input validation / AST filtering.**
   Parse the submitted code, reject anything that looks dangerous (imports of
   `os`, `subprocess`, `socket`, etc.). Rejected. AST filtering is a
   cat-and-mouse game that researchers have broken repeatedly. There is no
   complete, safe-by-construction allow-list for Python. It gives a false
   sense of security.

2. **Restricted subprocess: run code as a subprocess of the server with
   `subprocess.run(["python", "code.py"])`, no container.**
   Better than `exec()` — subprocess inherits less state — but the child
   process still has full access to the host filesystem, host network, and
   installed packages. Memory and CPU limits require platform-specific tricks
   (`resource.setrlimit` on Linux, nothing equivalent on Windows). Rejected
   as insufficient isolation.

3. **Paid cloud sandbox: Modal, AWS Lambda, or similar.**
   Genuine process and network isolation, managed scaling, no infrastructure
   to maintain. Cost is nonzero and requires an account/API key. Rejected for
   a portfolio project for two reasons: (a) adds a hard external dependency
   and a cost line item with no runtime budget, (b) a hiring manager cannot
   run this locally to reproduce results.

4. **Docker container isolation (local).** Run each execution inside a
   `docker run --rm` container with `--network none`, memory and CPU caps,
   and a hard wall-clock timeout enforced by killing the container. The
   container runs a minimal, pinned image that has no access to host paths
   except the per-request temporary directory. **Chosen.**

**What Docker gives us:**

- **Process isolation:** the user's code runs in a separate OS namespace with
  its own PID tree, filesystem root, and user space. It cannot see or affect
  the server process or other containers.
- **Network isolation:** `--network none` removes all network interfaces
  except loopback. The submitted code cannot make HTTP requests, open sockets,
  or exfiltrate data.
- **Resource caps:** `--memory 256m` and `--cpus 0.5` are enforced by the
  Linux kernel's cgroup subsystem (via Docker). They cannot be bypassed from
  inside the container.
- **Hard timeout:** `subprocess.run(..., timeout=15)` kills the `docker run`
  client process after 15 seconds; we then call `docker kill <name>` to stop
  the container itself. The container is gone in at most ~15 seconds regardless
  of what the submitted code does.
- **Automatic cleanup:** `--rm` removes the container and its writable layer
  immediately after the main process exits. No leftover state.
- **Non-root user inside the container:** the sandbox image creates a
  `sandbox` user; submitted code cannot install packages or write outside
  the mounted `/workspace` directory.

**Why local Docker and not a paid sandbox:**
This is a portfolio project with no runtime budget. Docker is free, runs on
any developer laptop and any CI environment, and lets an interviewer clone the
repo and reproduce the behaviour with a single `docker build` command. The
security properties are the same as a managed sandbox — both ultimately use
Linux kernel namespaces and cgroups. The difference is operational: managed
sandboxes add autoscaling and billing; local Docker adds a setup step.

**Consequences:**
- The host must have Docker installed and the daemon running. If it is not,
  the endpoint returns HTTP 503 with a clear message — it never silently falls
  back to the unsafe `exec()` path.
- The sandbox image (`photon-sandbox`) must be built once before the endpoint
  works: `docker build -t photon-sandbox docker/sandbox/`.
- Cold start per request: ~0.5–1 s on a warm Docker daemon for container
  spin-up. Acceptable for notebook execution; not suitable for sub-100 ms APIs.
- The `timeout` field is removed from the request model. Timeout is now a
  server-side constant (15 s), not a caller-controlled parameter. Callers
  should not be able to extend their own execution window.

---

## ADR-001 — Security hardening is a blocking prerequisite, not backlog

**Date:** 2026-06-21
**Status:** Accepted

**Context:** Initial audit of the existing codebase found: an API key committed
to the public repo in plaintext, a `/execute` endpoint that runs arbitrary
submitted code via in-process `exec()` with no sandboxing (full remote code
execution), and an execution `timeout` parameter that is accepted by the API but
never actually enforced.

**Decision:** No new feature work (RAG upgrades, AWS pipeline, anything) starts
until these are fixed. Security fixes are Phase 0.

**Alternatives considered:** Deferring security work until after the
architecture pivot, on the basis that it's a "dev-only" prototype. Rejected —
the repo is public right now, and "I found and fixed an RCE before building
further" is a stronger interview story than leaving it as a known issue.

**Consequences:** Slower start on the more exciting architecture work, but a
defensible, narratable security story.

---

## ADR-002 — Generalize beyond NASA-only scope

**Date:** 2026-06-21
**Status:** Proposed — not yet accepted, under active discussion

**Context:** Original project was a search + notebook generator scoped entirely
to NASA open datasets. Feedback from a NASA data science lead: technically
sound, but not a gap NASA itself doesn't already have internally covered — and
not generalized enough to demonstrate broad applicability for a job search
spanning AI Engineer / Data Engineer / Data Scientist / Data Analyst roles.

**Options on the table:**
1. Stay NASA-specific, publish findings as a paper instead of a product (the
   lead's suggestion) — rejected for the job-search goal, since a paper doesn't
   demonstrate shipped engineering the way a repo does.
2. Generalize into a two-pillar system: Pillar 1 = multi-source RAG discovery +
   LLM-grounded code generation (upgrades existing search/template code into a
   real RAG pipeline); Pillar 2 = "promote to pipeline" productionization layer
   on AWS (net-new, the data engineering half). Keep NASA as one of several
   built-in data source connectors rather than removing it.
3. A narrower scope: ship Pillar 1 only, to a genuinely polished and deeply
   understood state, and treat Pillar 2 as an explicit "v2" rather than building
   both in parallel at lower fidelity.

**Open question driving this decision:** given the actual goal is interview
readiness (not GitHub stars or a product launch), depth and the ability to
defend every design choice matters more than breadth. Leaning toward option 3
as a sequencing strategy under option 2's eventual architecture — i.e. build
toward the two-pillar vision, but ship and deeply learn Pillar 1 first rather
than racing to build both at once.

**Status:** Will be updated to Accepted once the scope conversation with the
project owner concludes.

---

## ADR-004 — Use git-filter-repo (not filter-branch) to scrub leaked secrets from history

**Date:** 2026-06-21
**Status:** Accepted

**Context:** The API key `h9Yf4aL8eITjxqeWPBvXyd3laRJB3eDu` was committed
to the public repo inside `photon/data/api_keys.json`. Removing the file from
the working tree and `.gitignore`-ing it is not enough — git stores every past
snapshot, so the key remained visible in commit history via `git log -p`.

**Options considered:**

1. **Rotate only, don't scrub history.** Generate a new key, remove the old
   one from the file, untrack it going forward. The old key still lives in git
   history forever. Rejected — the repo is public, so "it's in the history"
   is identical to "it's in plaintext on the internet."

2. **`git filter-branch`** (built-in). The traditional tool for rewriting
   history. Extremely slow on repos with many commits, error-prone to script
   correctly, and explicitly deprecated by the Git project. Rejected.

3. **BFG Repo Cleaner.** Fast Java-based tool purpose-built for removing
   secrets/large files. Good choice but requires a JVM and is less general
   than filter-repo. Would have been a valid pick.

4. **`git filter-repo`** — the Git project's official recommended replacement
   for filter-branch. Pure Python, fast (rewrote 34 commits in ~14 seconds),
   single pip install, and the command is easy to reason about:
   `--path <file> --invert-paths` means "rewrite history removing this path."
   **Chosen.**

**Consequences:** All commit SHAs changed after the rewrite. Required a
`git push --force` to GitHub. Safe here because the repo has no other
contributors and no known forks. After a force-push, GitHub retains the old
objects for up to 90 days in its cache — treat the old key as permanently
compromised regardless, which is why key rotation was done first.

---

## ADR-003 — Project memory and documentation workflow

**Date:** 2026-06-21
**Status:** Accepted

**Context:** Project owner is learning hands-on via Claude Code and needs (a)
context to persist across sessions without manual re-explanation, and (b) to be
able to explain every part of the project end-to-end in interviews.

**Decision:** Adopt a three-file documentation system: `CLAUDE.md` (stable
rules, auto-loaded every session), `docs/DECISIONS.md` (this file — durable
rationale), `docs/PROGRESS.md` (chronological session log). Commit and push
after every meaningful change, by default, without being asked each time.

**Alternatives considered:** A single combined README-as-memory file —
rejected, because mixing stable rules with a constantly-changing plan makes the
stable parts harder to trust and the changing parts harder to find.

**Consequences:** Slightly more upfront structure than "just start coding," but
removes the two biggest risks for this project: losing context between
sessions, and being unable to articulate decisions later.
