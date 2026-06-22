# Architecture decisions log

Append-only. Each entry is numbered and dated, and once written, is not edited —
if a decision changes, add a new ADR that supersedes it and say so. Status is one
of: Proposed, Accepted, Superseded.

This file exists for one reason: when someone asks "why did you build it that
way," the honest answer — including the options you rejected — should already be
written down, not reconstructed from memory under interview pressure.

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
