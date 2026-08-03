from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_patient
from app.database.postgres import get_db
from app.models.alert import Alert
from app.models.patient import Patient
from app.schemas.alert import AlertOut

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertOut])
def list_alerts(
    resolved: bool = False,
    patient: Patient = Depends(get_current_patient),
    db: Session = Depends(get_db),
):
    return (
        db.query(Alert)
        .filter(Alert.patient_id == patient.id, Alert.resolved == resolved)
        .order_by(Alert.created_at.desc())
        .all()
    )


@router.post("/{alert_id}/resolve", response_model=AlertOut)
def resolve_alert(alert_id: str, patient: Patient = Depends(get_current_patient), db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id, Alert.patient_id == patient.id).first()
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
    alert.resolved = True
    db.commit()
    db.refresh(alert)
    return alert
