import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_patient
from app.database.postgres import get_db
from app.models.document import Document
from app.models.patient import Patient
from app.schemas.document import DocumentOut
from app.services import document_service

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=list[DocumentOut])
def list_documents(patient: Patient = Depends(get_current_patient), db: Session = Depends(get_db)):
    return (
        db.query(Document)
        .filter(Document.patient_id == patient.id)
        .order_by(Document.uploaded_at.desc())
        .all()
    )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: uuid.UUID,
    patient: Patient = Depends(get_current_patient),
    db: Session = Depends(get_db),
):
    """Deletes the document plus everything derived from it: its visit,
    medications, lab results, doctor note, alerts, timeline events, Chroma
    embeddings, and the stored file. See document_service for the cascade
    order and why allergies are left untouched."""
    document = (
        db.query(Document)
        .filter(Document.id == document_id, Document.patient_id == patient.id)
        .first()
    )
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    document_service.delete_document(db, document)
