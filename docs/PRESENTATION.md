# MediSync AI — Presentation Script (4-5 minutes)

## Slide 1: Title (30 sec)

"MediSync AI — an AI-powered medical document intelligence platform. We turn scattered PDFs into structured insights, safety alerts, and evidence-backed answers."

## Slide 2: The Problem (30 sec)

"Patients receive lab reports, prescriptions, and discharge summaries as PDFs. Finding drug interactions, tracking lab trends, or understanding why a doctor changed medication requires manual review across dozens of documents."

## Slide 3: Our Approach (45 sec)

"We built a dual-database architecture. PostgreSQL stores structured facts — medications, labs, visits. ChromaDB stores document chunks for semantic search. Critically, we separate deterministic logic from AI reasoning."

## Slide 4: Architecture Diagram (30 sec)

"Upload flows through OCR, classification, and entity extraction. Data lands in PostgreSQL and ChromaDB. A rule engine runs deterministic safety checks. RAG powers the chat interface."

## Slide 5: Rule Engine Demo (60 sec)

"Watch what happens when we upload a prescription for Amoxicillin to a patient allergic to Penicillin. The rule engine — not the LLM — flags this as critical. The LLM only explains why. Same for duplicate prescriptions, dosage conflicts, and lab trends."

**Live demo:** Upload Prescription.txt → show allergy alert on dashboard.

## Slide 6: Timeline & Charts (30 sec)

"Every document builds a chronological timeline — visits, medications, labs. Lab trends are visualized with Recharts. An algorithm detects increasing blood sugar; the LLM explains the clinical significance."

**Live demo:** Show timeline and blood sugar chart.

## Slide 7: RAG Chat (45 sec)

"Ask 'Why did my doctor change my medicine?' The system retrieves relevant document chunks, combines them with structured data, and generates an answer with evidence citations and a confidence score."

**Live demo:** Ask a question in chat → show evidence panel.

## Slide 8: Tech Stack & Deployment (30 sec)

"React frontend on Vercel. FastAPI backend on Render. PostgreSQL plus ChromaDB. Ollama locally, Groq in production. LangChain for RAG orchestration."

## Slide 9: Closing (15 sec)

"MediSync AI demonstrates production-quality architecture — deterministic safety rules plus AI explanation. Not a hackathon prototype, but a foundation for real medical document intelligence."

## Q&A Prep

- **Why two databases?** Structured queries vs semantic search serve different needs.
- **Why not let the LLM check interactions?** LLMs hallucinate; patient safety requires deterministic rules.
- **HIPAA?** Current version is a demo; production would need encryption, audit logs, and BAA-compliant hosting.
