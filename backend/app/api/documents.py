from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_patient
from app.database.postgres import get_db
from app.models.document import Document
from app.models.patient import Patient
from app.schemas.document import DocumentOut

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=list[DocumentOut])
def list_documents(patient: Patient = Depends(get_current_patient), db: Session = Depends(get_db)):
    return (
        db.query(Document)
        .filter(Document.patient_id == patient.id)
        .order_by(Document.uploaded_at.desc())
        .all()
    )
