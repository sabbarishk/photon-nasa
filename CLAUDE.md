# Photon — project memory

This file is read automatically at the start of every Claude Code session.
Keep it short and stable — rules and facts only. Anything that changes often
goes in docs/PROGRESS.md. Rationale for decisions goes in docs/DECISIONS.md.
Stay under ~150 lines.

---

## What Photon is — one sentence

Photon is an open-source AI analysis assistant: describe what you want to know
about your data in plain English, and Photon writes the analysis code, runs it
against your actual data in a sandboxed environment, and returns real results
alongside the code that produced them and the methodology reasoning behind it.

## The core differentiator

Every other LLM tool generates code but does not run it. Photon executes
against real data. The result is not hallucinated — it comes from actual
execution. That execution layer is the trust mechanism, and the Docker sandbox
we already built is the entire product differentiator, not just a security fix.

The RAG layer retrieves analysis methodology playbooks (not datasets) based on
automatic data profiling. The LLM writes analysis grounded in retrieved
methodology, not generic pandas instincts. This is what makes the approach
appropriate for the data type, not just syntactically correct.

## Target audience

Any data practitioner — analyst, scientist, engineer — who wants to go from
"I have this data and a question" to "here is a real, executed, trustworthy
result with the code and methodology visible" without copying code into a
notebook manually.

## Two pillars — build in sequence, not in parallel

**Pillar 1 (build now):** Data profiling → methodology retrieval (RAG) →
LLM code generation → Docker execution → real results returned.
Status: execution sandbox done. RAG layer and LLM generation are Phase 2.

**Pillar 2 (after Pillar 1 is solid):** One-click promotion of a working
analysis to a scheduled AWS pipeline with monitoring and data quality checks.
Status: planned. Do not start until Pillar 1 is interview-ready.

## Current tech stack

- Backend: Python 3.11, FastAPI
- Embeddings: sentence-transformers (all-MiniLM-L6-v2), local inference
- Vector store: ChromaDB (persistent, cosine similarity, HNSW index)
- Code execution: Docker container sandbox (python:3.11-slim, --network none,
  256MB RAM, 0.5 CPU, 15s hard timeout via subprocess + docker kill)
- LLM: Anthropic Claude API (claude-sonnet-4-6) — NOT YET WIRED IN
- Frontend: React + Vite (single frontend/ directory at repo root)
- Data input: any — CSV upload, URL, or built-in NASA dataset examples

## What is NOT built yet (Phase 2 — do not invent it)

- Data profiling (schema detection, type inference, null analysis)
- Methodology playbook knowledge base in ChromaDB
- LLM call for code generation (llm.py does not exist yet)
- Workflow route wired to LLM (still uses deleted Jinja2 templates)
- Frontend data upload UI
- Any AWS infrastructure

## Non-negotiables — never regress these

- No secrets, API keys, or .env files committed. Ever.
- No in-process exec() for user code. The Docker sandbox is mandatory.
- No empty stub files that look implemented but are hollow.
- No fallback to unsafe execution paths if Docker is unavailable — return 503.
- API keys never stored or compared in plaintext.

## Workflow rules — every session, without being asked

1. Commit after every meaningful change. Conventional Commits:
   feat: / fix: / docs: / refactor: / security: / chore:
   One logical change per commit.
2. Push after every commit.
3. Update docs/PROGRESS.md at session end — what changed, what's next.
   Newest entry on top.
4. Log non-trivial decisions in docs/DECISIONS.md before implementing them.
   If you're unsure whether something counts, log it — this file is interview
   prep material.
5. Explain every change in plain language as you go. The project owner is
   learning hands-on and must be able to defend every decision in an interview.
6. All commits are authored solely under the git identity already configured
   (sabbarishk). Do not add Co-Authored-By lines.

## Reference

- README.md — human-facing project overview
- docs/DECISIONS.md — why we chose what we chose (ADR format, append-only)
- docs/PROGRESS.md — chronological session log
- docker/sandbox/Dockerfile — execution sandbox image
- photon/app/services/vector_db.py — ChromaDB retrieval layer
- photon/app/routes/execute.py — Docker execution endpoint
