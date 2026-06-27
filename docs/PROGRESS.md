# Progress log — Photon v2

Newest entry on top. "What happened" lives here.
"Why we decided it" lives in DECISIONS.md.

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
