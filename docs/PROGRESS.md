# Progress log

Chronological. One entry per work session, newest entry on top. This is the
"what happened and when" record — rationale for *why* belongs in DECISIONS.md,
not here.

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
