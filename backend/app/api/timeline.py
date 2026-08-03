"""GET /timeline reads the materialized TimelineEvent table (populated by
services.timeline_service.build_timeline_for_visit at upload time), matching
the frontend's TimelineEvent contract exactly (id, event_type, event_date,
payload, visit_id)."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_patient
from app.database.postgres import get_db
from app.models.patient import Patient
from app.models.timeline_event import TimelineEvent
from app.schemas.timeline import TimelineEventOut

router = APIRouter(prefix="/timeline", tags=["timeline"])


@router.get("", response_model=list[TimelineEventOut])
def get_timeline(patient: Patient = Depends(get_current_patient), db: Session = Depends(get_db)):
    return (
        db.query(TimelineEvent)
        .filter(TimelineEvent.patient_id == patient.id)
        .order_by(TimelineEvent.event_date.desc())
        .all()
    )
