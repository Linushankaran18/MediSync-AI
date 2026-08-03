"""RAG chat: retrieve patient-scoped chunks from Chroma + structured PG facts
(via timeline_service.fetch_structured_summary), call the LLM with strict
"answer only from context, cite sources" instructions, score confidence, and
persist the exchange."""
import uuid

from sqlalchemy.orm import Session

from app.ai.llm import rag_answer
from app.models.alert import Alert
from app.models.chat_history import ChatHistory
from app.models.document import Document
from app.services import embedding_service, timeline_service
from app.services.confidence_service import compute_confidence


def _format_chunks(hits: list[dict]) -> str:
    if not hits:
        return "(no relevant document excerpts found)"
    blocks = []
    for h in hits:
        meta = h["metadata"]
        blocks.append(
            f"[document_id={meta['document_id']} doc_type={meta['doc_type']} "
            f"visit_date={meta.get('visit_date') or 'unknown'}]\n{h['text']}"
        )
    return "\n\n---\n\n".join(blocks)


def answer_question(db: Session, patient_id, question: str) -> dict:
    hits = embedding_service.query_patient_documents(patient_id, question, n_results=5)
    structured_context = timeline_service.fetch_structured_summary(db, patient_id)
    retrieved_chunks = _format_chunks(hits)

    answer_text = rag_answer(question, structured_context, retrieved_chunks)

    doc_ids = {h["metadata"]["document_id"] for h in hits}
    avg_ocr_quality = None
    if doc_ids:
        docs = db.query(Document).filter(Document.id.in_([uuid.UUID(d) for d in doc_ids])).all()
        qualities = [d.ocr_quality for d in docs if d.ocr_quality is not None]
        avg_ocr_quality = sum(qualities) / len(qualities) if qualities else None

    has_conflicting_alerts = (
        db.query(Alert)
        .filter(Alert.patient_id == patient_id, Alert.resolved.is_(False), Alert.severity.in_(["critical", "major"]))
        .count()
        > 0
    )

    confidence = compute_confidence(avg_ocr_quality, hits, has_conflicting_alerts, answer_text)

    evidence = [
        {
            "document_id": h["metadata"]["document_id"],
            "snippet": h["text"][:280],
            "visit_date": h["metadata"].get("visit_date") or None,
        }
        for h in hits
    ]

    disclaimer = (
        "This is an AI summary of your own records for informational purposes only. "
        "It is not a diagnosis. Please confirm anything important with your doctor or pharmacist."
    )

    db.add(
        ChatHistory(
            patient_id=patient_id,
            question=question,
            answer=answer_text,
            evidence=evidence,
            confidence=confidence / 100,
        )
    )
    db.commit()

    return {"answer": answer_text, "evidence": evidence, "confidence": confidence, "disclaimer": disclaimer}
