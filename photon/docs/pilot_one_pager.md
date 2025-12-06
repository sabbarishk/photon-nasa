# Photon — Pilot / Investor One-Pager

Product: Photon — Natural Language Query + Automated Workflow Generator for Earth science datasets (NASA-ready)

Problem
- Researchers and agencies must stitch multiple open Earth-data sources into reproducible analysis workflows. That process is slow, error-prone, and requires deep domain and tooling knowledge.

Solution
- Photon accepts natural-language queries, returns relevant datasets and curated metadata, and auto-generates runnable analysis notebooks (Python/Jupyter) tailored to the dataset format (CSV/NetCDF/HDF5). Local embedding fallback keeps it usable without paid LLM access.

MVP (what exists now)
- FastAPI backend with `/query` and `/workflow/generate` endpoints
- File-based vector store & NASA CMR ingest script (sample MODIS + GISS demo)
- Local embeddings via `sentence-transformers` and HF router fallback
- Demo notebooks and helper scripts to generate/save notebooks

Target customers / early adopters
- University Earth/Climate research groups
- Government data teams (NASA, NOAA, ESA partner groups)
- Climate analytics startups and consulting firms

Traction / validation
- Working prototype that can ingest NASA metadata and generate analysis notebooks from live dataset URLs (demo with GISS CSV).
- Ready to run pilot integrations and custom workflow templates.

Ask (pilot & seed)
- Pilot stage: $50k–$150k for 3–6 month paid pilots (integration, customization, and support for 1–3 customers).
- Seed ask (recommended): $500k to convert the MVP into a production-ready hosted offering and land multiple pilots.

Use of funds (example $500k seed)
- Engineering: core backend hardening, API auth, CI/CD, integration with a managed vector DB — $180k
- Product & UX: build a small frontend for dataset discovery and notebook preview — $80k
- Infrastructure & managed services: vector DB, hosting, monitoring — $60k
- Pilot integrations & professional services (customer SOWs) — $80k
- Business, legal, and go-to-market (docs, one-pager, outreach) — $40k
- Operating buffer / hires (6–9 months runway) — $60k

Milestones (9 months)
1. Ship hardened API, auth, and managed vector DB integration (Months 1–3)
2. Close 2 paid pilots and deliver custom templates (Months 3–6)
3. Launch simple SaaS onboarding + pricing page; target research labs and agencies (Months 6–9)

Key metrics to prove
- Pilot to paid conversion rate; Monthly Recurring Revenue (MRR); time-to-first-query for pilots; retention of pilot customers.

Contact / next steps
- I can produce a short budget spreadsheet, an outreach email template for pilot prospects, and a CLI to run batch notebook generation for pilot demos. Which should I produce next?
