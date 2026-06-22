# Photon — project memory

This file is read automatically at the start of every Claude Code session. Keep it
short and stable — rules and facts only. Anything that changes often (plans, status,
history) goes in docs/PROGRESS.md. Anything that needs a rationale goes in
docs/DECISIONS.md. This file should stay under ~150 lines.

## What this project is

Photon started as a natural-language search + Jupyter notebook generator for NASA
open datasets. It is being generalized and hardened into a portfolio-grade project
for job applications (AI Engineer / Data Engineer / Data Scientist / Data Analyst
roles). Primary goal: technical depth a hiring manager can interrogate end-to-end —
not GitHub stars, not a SaaS launch.

The exact target architecture is still being decided — see docs/DECISIONS.md
ADR-002 for the live status before assuming scope.

## Tech stack (current)

- Backend: Python 3.11, FastAPI
- Embeddings: sentence-transformers (all-MiniLM-L6-v2), local inference
- Vector store: flat JSON file with NumPy cosine search (not yet a real vector DB)
- Notebook generation: Jinja2 templates (static — not yet LLM-generated)
- Code execution: in-process `exec()` (NOT sandboxed — see Non-negotiables below)
- Frontend: React + Vite
- Planned additions: LLM-grounded code generation, AWS-based productionization layer

## Non-negotiables (do not regress these, even temporarily)

- Never commit secrets, API keys, or `.env` files. If you generate or rotate a key
  during a session, it goes in an untracked file or environment variable, never in
  a file that gets committed.
- The `/execute` endpoint must never run arbitrary code via in-process `exec()`
  without sandboxing (container isolation, resource limits, enforced wall-clock
  timeout). This was the #1 finding of the initial security audit. Until it's
  fixed, treat the existing `execute.py` as known-broken, not a pattern to copy.
- Auth: API keys are never stored or compared in plaintext in new code. Don't
  reintroduce `PHOTON_SKIP_AUTH`-style bypasses outside of clearly marked local
  dev paths.
- No empty stub files left in the codebase pretending to be implemented
  (`llm.py`, `embedding.py`, `vector_db.py` were empty — either build them or
  delete them, never leave a 0-byte file that looks finished).

## Workflow rules (always do these, every session)

1. **Commit after every meaningful change.** Use Conventional Commits style:
   `feat:`, `fix:`, `docs:`, `refactor:`, `security:`, `chore:`. One logical
   change per commit — don't batch unrelated edits.
2. **Push after every commit**, unless explicitly told to hold off (e.g. mid
   experiment on a throwaway branch).
3. **Update `docs/PROGRESS.md`** at the end of every session — what changed, what
   was found, what's next. Newest entry on top.
4. **Log non-trivial decisions in `docs/DECISIONS.md`** — anything where there
   were real alternatives (a library choice, an architecture pattern, a security
   trade-off). If you're not sure whether something counts, ask rather than skip
   it; this file is the interview prep material.
5. **Explain as you go.** The person you're working with is learning hands-on and
   needs to be able to defend every part of this project in an interview. Don't
   just make changes — say what you changed and why in plain language before
   moving on.

## Reference docs

- `README.md` — human-facing overview, what it is and how to run it
- `docs/DECISIONS.md` — why we chose what we chose (ADR-style, append-only)
- `docs/PROGRESS.md` — chronological session log
