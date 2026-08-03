# MedIntel AI — Technical Report

## 1. Executive Summary

MedIntel AI is an AI-powered medical document intelligence platform that transforms unstructured medical PDFs into structured patient data, safety alerts, timelines, and evidence-backed conversational answers. The system separates **deterministic medical logic** (rule engine) from **AI reasoning** (LLM for extraction and explanation), producing a production-quality architecture suitable for real-world healthcare document management.

## 2. Problem Statement

Patients accumulate medical documents across visits — lab reports, prescriptions, discharge summaries, and doctor notes — stored as unstructured PDFs. Extracting actionable insights (medication conflicts, allergy risks, lab trends) manually is error-prone and time-consuming.

## 3. Solution Architecture

### 3.1 Dual Database Design

| Store | Purpose | Data Types |
|-------|---------|------------|
| PostgreSQL | Structured facts | Medications, labs, visits, allergies, alerts |
| ChromaDB | Semantic search | Document chunks with BGE embeddings |

This separation ensures deterministic queries (timeline, trends, rules) run against relational data while RAG retrieval searches unstructured text.

### 3.2 Processing Pipeline

1. **Upload** → PDF stored on disk
2. **OCR** → Text extraction (pypdf → pdfplumber fallback)
3. **Classification** → LLM assigns document type
4. **Entity Extraction** → LLM returns structured JSON
5. **Persistence** → PostgreSQL + ChromaDB chunks
6. **Rule Engine** → Deterministic safety checks
7. **Timeline** → Chronological event generation

### 3.3 Rule Engine (Deterministic Core)

The rule engine never delegates safety decisions to the LLM:

- **Drug Interactions:** Static knowledge base of ~50 common pairs
- **Allergy Cross-Reactivity:** Penicillin → Amoxicillin mapping with fuzzy matching
- **Duplicate Prescriptions:** Same drug across visits
- **Dosage Conflicts:** Conflicting doses/frequencies
- **Lab Trends:** Monotonic increase/decrease over 3+ data points

### 3.4 RAG Pipeline

User questions → embed query → ChromaDB retrieval (patient-scoped) → LLM answer with evidence citations → confidence score.

Confidence computed from: OCR quality (25%) + retrieval quality (25%) + rule consistency (25%) + answer completeness (25%).

## 4. Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | React, Vite, Tailwind, Recharts |
| Backend | FastAPI, SQLAlchemy, LangChain |
| Database | PostgreSQL, ChromaDB |
| Embeddings | BAAI/bge-small-en-v1.5 |
| LLM | Ollama (local) / Groq (cloud) |
| Auth | JWT with bcrypt |

## 5. Security & Compliance

- JWT authentication with patient-scoped data access
- LLM prompts enforce "never diagnose" policy
- Confidence below 70% triggers doctor consultation recommendation
- All answers cite source document evidence

## 6. Results & Demo

Demo account includes:
- Penicillin allergy + Amoxicillin prescription → critical alert
- Blood sugar trend: 120 → 145 → 170 → increasing trend alert
- Full timeline with visits, medications, and lab results

## 7. Future Work

- FHIR integration for EHR connectivity
- Multi-patient support per provider account
- Real-time WebSocket upload progress
- HIPAA-compliant deployment on AWS/GCP
- Fine-tuned medical NER model replacing generic LLM extraction
