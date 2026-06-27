# Progress log — Photon v2

Newest entry on top. "What happened" lives here.
"Why we decided it" lives in DECISIONS.md.

---

## 2026-06-27 — Session 9: Phase 1 conversational backend complete

**Did:**
- Added conversation_history (list) and session_id (str) to WorkflowRequest
- Added PHOTON_SUMMARY: marker parsing — generated code prints a JSON block
  that gets parsed into kpi_cards and anomalies without crashing on failure
- Updated generate_analysis_code(): conversation history injected as first
  prompt section (last 6 turns, 2 lines each), dashboard prompt replaces
  single-chart prompt (2-4 subplots, dark_background, #6366f1 accent,
  plt.savefig with facecolor=#09090b)
- Added generate_insight_narrative(): second LLM pass, max_tokens=300,
  returns "" on any failure — never crashes main pipeline
- Added generate_follow_up_suggestions(): third LLM call, returns list of 3
  strings, has safe defaults per data_type on failure
- Wired full pipeline in workflow.py: code → execute → parse → narrative →
  suggestions → structured response with all 8 fields
- Added Excel (.xlsx) support to load_dataframe(): URL and local path,
  using pd.read_excel(io.BytesIO(resp.content)) for URLs
- Added openpyxl to requirements.txt
- Fixed Lambda URL loading: changed prompt from requests.get() to
  pd.read_csv(url) directly — requests not in Lambda data science layer
- Increased max_tokens for code generation: 2500 → 4000 (prevents truncation
  on larger dashboard code with 4 subplots + PHOTON_SUMMARY block)
- Added prompt safety rules: no TwoSlopeNorm/DivergingNorm, no wide heatmaps,
  wrap zero-division risks, use proven chart types only

**Test 1 results (no history, airtravel.csv):**
- kpi_cards: 5 items (Overall Avg, Peak, Lowest, Growth %, Peak Season Month)
- insight_narrative: 5 sentences, specific numbers, business-ready language
- follow_up_suggestions: 3 specific questions using column names
- execution.exit_code: 0
- execution.output_image: YES (328,864 char base64 PNG)
- anomalies: [] (correctly empty — data is clean)

**Test 2 results (with history, follow-up question):**
- Narrative correctly references prior context (25% growth, peak month)
- Suggestions build on prior analysis (FEB vs AUG comparison, growth drivers)
- kpi_cards: 5 items focused on monthly comparison (new question's angle)
- execution.exit_code: 0, output_image: YES (398,548 char base64 PNG)

**Key things to know for interviews:**
- The PHOTON_SUMMARY: marker is a sentinel pattern — the LLM is instructed to
  print it as the last line of stdout. We split on the marker and parse JSON.
  If anything fails (LLM didn't print it, JSON is malformed), we return [].
  Never crash the pipeline over a parse failure.
- Two LLM passes per turn: pass 1 generates code (max 4000 tokens), pass 2
  generates insight narrative (max 300 tokens). Separated so each LLM can
  focus — code generation is about correctness, narrative is about communication.
- Client-side conversation history: passed per request, stateless backend.
  No Redis, no sessions, no server-side state. Self-hostable by design.
- Lambda doesn't have requests installed — pandas reads URLs directly via
  urllib internally. The prompt explicitly says "do NOT use requests".

**What's done in v2 so far:**
- [x] Conversation memory: message history passed per turn
- [x] Multi-panel dashboard code generation (2-4 charts)
- [x] KPI card extraction from PHOTON_SUMMARY marker
- [x] Second LLM pass: AI insight narrative generation
- [x] Follow-up suggestion generation (third LLM call)
- [x] Excel file support (.xlsx via openpyxl)
- [x] Structured response format: all 8 fields
- [ ] Anomaly detection (currently empty — generated code rarely finds them)
- [ ] Executive UI (Phase 2)
- [ ] Demo mode and landing page (Phase 2)
- [ ] Pillar 2 (Phase 3)

**Next session:**
Phase 2 — Executive UI. Read docs/DESIGN.md first.
Build: split-panel workspace, KPI card components, multi-chart display,
insight narrative panel, follow-up suggestion chips, landing page.

---

## 2026-06-27 — Direction reset: v2 planning session

**What changed:**
- Identified that v1 failed on three core constraints:
  no conversational memory, beginner UI, Pillar 2 never built
- Locked final v2 direction: open-source conversational data analyst
- Rewrote all three memory files with locked constraints
- All future sessions must use Claude Sonnet 4.6 HIGH

**What v2 is:**
Open-source self-hostable conversational data analyst. Upload CSV/Excel
or paste URL. Ask questions. Get a full KPI dashboard — cards, charts,
anomalies, AI insight narrative. Follow up and the analysis refines.
Every result is executed against real data on AWS Lambda. Nothing
hallucinated. Self-hostable. Free. The open-source Julius AI alternative.

**What carries forward from v1 (keep, don't rebuild):**
- ChromaDB RAG layer with methodology playbooks ✓
- Data profiler (type detection, schema, nulls) ✓
- AWS Lambda execution (512MB, 30s, PYTHONPATH fix) ✓
- Anthropic API integration with load_dotenv ✓
- FastAPI backend structure ✓
- All security work (key rotation, sandbox, IAM) ✓
- All ADRs and documentation ✓

**What must be built in v2 (in this order):**

PHASE 1 — Conversational backend (most critical)
- [ ] Conversation memory: message history passed per turn
- [ ] Multi-panel dashboard code generation (2-4 charts)
- [ ] KPI card extraction from execution output
- [ ] Second LLM pass: AI insight narrative generation
- [ ] Anomaly detection and callout
- [ ] Follow-up suggestion generation
- [ ] Excel file support (.xlsx via openpyxl)
- [ ] Structured response format for all of the above

PHASE 2 — Executive UI
- [ ] Landing page with demo mode
- [ ] Split-panel workspace (conversation left, dashboard right)
- [ ] KPI card components
- [ ] Multi-chart display
- [ ] Insight narrative display
- [ ] Anomaly callout display
- [ ] Follow-up suggestion chips (clickable)
- [ ] Drag-and-drop file upload
- [ ] Demo mode with synthetic manufacturing dataset
- [ ] Zero NASA branding anywhere

PHASE 3 — Data engineering pipeline (Pillar 2)
- [ ] S3 storage for analysis results
- [ ] Step Functions orchestration
- [ ] CloudWatch monitoring and alerting
- [ ] "Promote to pipeline" feature
- [ ] Pipeline dashboard

**Next session task:**
Start Phase 1. Build the conversational backend properly.
First task: update workflow.py to accept and pass conversation history.
Second task: update llm.py to use conversation history in prompt.
Third task: add second LLM pass for insight narrative.
Fourth task: structured response format.

---

## 2026-06-27 — Session 8: First end-to-end test confirmed working

**Result:** Full pipeline confirmed working end to end:
- Profiler detected 12 rows × 4 cols correctly
- ChromaDB returned tabular playbook via metadata filter
- LLM generated 4-panel matplotlib analysis code
- Lambda executed with exit_code 0
- Base64 chart returned in response
- Frontend displayed profile card, methodology badge, chart, and code

**Known issues at this point:**
- Single-shot only — no conversation memory
- Single chart output — not a dashboard
- No insight narrative
- UI is beginner-level (basic Tailwind)
- NASA branding still in navbar and footer
- PHOTON_SKIP_AUTH=1 required for local dev
- Excel not supported

**Confirmed working infrastructure:**
- Lambda function: photon-code-executor (us-east-1, 512MB, 30s)
- Lambda layer: photon-data-science v2 (pandas/numpy/matplotlib)
- S3 bucket: photon-analysis-storage (us-east-1)
- IAM user: photon-local (lambda:InvokeFunction only)
- ChromaDB: persistent at photon/data/chroma/
- Playbooks: tabular.md, time_series.md, wide_format.md loaded

**Correct server start command:**
cd d:\Photon\photon_initial
$env:PHOTON_SKIP_AUTH="1"
uvicorn app.main:app --reload --app-dir photon

**Correct frontend start:**
cd d:\Photon\photon_initial\frontend
npm run dev
