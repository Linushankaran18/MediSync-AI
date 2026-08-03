# MedIntel AI

Patient document intelligence: upload prescriptions/lab reports/discharge summaries/doctor
notes, get structured extraction, drug-interaction & allergy alerts, a chronological
timeline, lab trend charts, and a RAG chat that answers only from the patient's own
records with cited evidence and a confidence score.

## Status

This build resumes and completes the original scaffold (Phase 1 - auth + schema
foundation - was already in place; this pass fills in documents/visits/medications/
labs/allergies/alerts/timeline/chat, wires the rule engine, and adds the previously
undeclared `DoctorNote` table referenced by the timeline service). See
`docs/TECHNICAL_REPORT.md` and `docs/PRESENTATION.md` for the full write-up and
demo script.

## Architecture

PostgreSQL holds structured facts (medications, labs, visits, allergies). ChromaDB
holds text chunks for RAG. A deterministic rule engine (not the LLM) decides
interactions/allergies/duplicates/dosage conflicts/lab trends; the LLM only explains
findings and answers chat questions from retrieved evidence - it never diagnoses.

LLM: Ollama locally (`LLM_PROVIDER=ollama`), Groq in production (`LLM_PROVIDER=cloud`,
matches `render.yaml`), via LangChain's `ChatOllama`/`ChatOpenAI` with
`with_structured_output` for forced-schema extraction. Embeddings: `bge-small-en-v1.5`
(sentence-transformers, local, free). OCR: `pypdf` primary, `pdfplumber` fallback;
plain `.txt` uploads (the demo sample docs) are read directly.

## Quick start (local, no Docker)

Requires a running Postgres (`DATABASE_URL`) and either a local Ollama
(`ollama pull qwen3:8b`) or a Groq API key.

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env
alembic upgrade head
python scripts/seed_demo.py   # optional: demo@medintel.ai / demo1234
uvicorn app.main:app --reload --port 8000
```

```bash
cd frontend
npm install
npm run dev
```

## Quick start (Docker)

```bash
cp .env.example .env
docker compose up --build
# first run only, in another shell:
docker compose exec ollama ollama pull qwen3:8b
```

Backend: http://localhost:8000/docs - Frontend: http://localhost:5173

## Deployment

Backend on Render (`render.yaml`, Docker + Groq cloud LLM), frontend on Vercel
(`frontend/vercel.json`).

## Demo data

`docs/sample-docs/*.txt` are the plain-text demo documents (Prescription, LabReport,
DoctorNote, DischargeSummary for patient "John Demo"). `backend/scripts/seed_demo.py`
inserts them directly via the ORM (no LLM/OCR calls needed) including a pre-seeded
critical allergy alert (penicillin allergy + amoxicillin) and a blood-sugar trend
(120 -> 145 -> 170).
