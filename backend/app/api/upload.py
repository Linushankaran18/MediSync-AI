import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import get_current_patient
from app.database.postgres import get_db
from app.models.document import Document
from app.models.patient import Patient
from app.schemas.document import UploadResponse
from app.services import embedding_service, interaction_service, ocr_service, parser_service

router = APIRouter(tags=["upload"])

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".png", ".jpg", ".jpeg"}


@router.post("/upload", response_model=UploadResponse)
def upload_document(
    file: UploadFile,
    patient: Patient = Depends(get_current_patient),
    db: Session = Depends(get_db),
):
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF, .txt, or image (.png/.jpg/.jpeg) uploads are supported",
        )

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    stored_name = f"{uuid.uuid4()}{ext}"
    stored_path = os.path.join(settings.UPLOAD_DIR, stored_name)
    with open(stored_path, "wb") as f:
        f.write(file.file.read())

    raw_text, ocr_quality = ocr_service.extract_text(stored_path)
    if not raw_text.strip():
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Could not extract any text from this document")

    extracted = parser_service.classify_and_extract(raw_text)

    document = Document(
        patient_id=patient.id,
        filename=file.filename,
        doc_type=extracted.doc_type,
        raw_text=raw_text,
        ocr_quality=ocr_quality,
        extracted_entities=extracted.model_dump(mode="json"),
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    parser_service.persist_extracted(db, patient.id, document.id, extracted)
    embedding_service.ingest_document(patient.id, document.id, extracted.doc_type, extracted.visit_date, raw_text)
    alerts = interaction_service.run_all_rules(db, patient.id, document.id)

    alert_note = f", {len(alerts)} alert(s) triggered" if alerts else ""
    message = f"Processed as {extracted.doc_type}{alert_note}."

    return UploadResponse(
        message=message,
        document_id=document.id,
        doc_type=extracted.doc_type,
        ocr_quality=ocr_quality,
        alerts_triggered=[a.alert_type for a in alerts],
    )
