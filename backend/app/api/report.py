from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_patient
from app.database.postgres import get_db
from app.models import Alert, Document, LabResult, Medication, Patient, Visit
from app.schemas import LabTrendResponse, SummaryResponse
from app.services.trend_service import get_lab_trend

router = APIRouter(tags=["analytics"])


@router.get("/lab-trends", response_model=LabTrendResponse)
def lab_trends(
    test: str = Query(default="blood_sugar"),
    patient: Patient = Depends(get_current_patient),
    db: Session = Depends(get_db),
):
    return get_lab_trend(db, patient.id, test)


@router.get("/summary", response_model=SummaryResponse)
def summary(
    patient: Patient = Depends(get_current_patient),
    db: Session = Depends(get_db),
):
    doc_count = db.query(Document).filter(Document.patient_id == patient.id).count()
    visit_count = db.query(Visit).filter(Visit.patient_id == patient.id).count()
    alert_count = (
        db.query(Alert)
        .filter(Alert.patient_id == patient.id, Alert.resolved.is_(False))
        .count()
    )
    med_count = (
        db.query(Medication)
        .join(Visit)
        .filter(Visit.patient_id == patient.id)
        .count()
    )
    lab_count = (
        db.query(LabResult)
        .join(Visit)
        .filter(Visit.patient_id == patient.id)
        .count()
    )
    recent = (
        db.query(Document)
        .filter(Document.patient_id == patient.id)
        .order_by(Document.uploaded_at.desc())
        .first()
    )
    return SummaryResponse(
        document_count=doc_count,
        visit_count=visit_count,
        active_alerts=alert_count,
        medication_count=med_count,
        lab_count=lab_count,
        recent_doc_type=recent.doc_type if recent else None,
    )
