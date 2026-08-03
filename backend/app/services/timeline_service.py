import uuid

from sqlalchemy.orm import Session

from app.models import Allergy, Document, LabResult, Medication, TimelineEvent, Visit


def _add_event(
    db: Session,
    patient_id: uuid.UUID,
    visit_id: uuid.UUID | None,
    event_type: str,
    event_date,
    payload: dict,
) -> None:
    db.add(
        TimelineEvent(
            patient_id=patient_id,
            visit_id=visit_id,
            event_type=event_type,
            event_date=event_date,
            payload=payload,
        )
    )


def build_timeline_for_visit(db: Session, patient_id: uuid.UUID, visit: Visit) -> None:
    _add_event(
        db,
        patient_id,
        visit.id,
        "visit",
        visit.visit_date,
        {"doctor": visit.doctor, "hospital": visit.hospital},
    )
    for med in visit.medications:
        _add_event(
            db,
            patient_id,
            visit.id,
            "medication",
            visit.visit_date,
            {"name": med.name, "dose": med.dose, "frequency": med.frequency},
        )
    for lab in visit.lab_results:
        _add_event(
            db,
            patient_id,
            visit.id,
            "lab_result",
            lab.test_date or visit.visit_date,
            {
                "test_name": lab.test_name,
                "value": lab.value,
                "unit": lab.unit,
            },
        )
    if visit.doctor_note:
        _add_event(
            db,
            patient_id,
            visit.id,
            "doctor_note",
            visit.visit_date,
            {"content": visit.doctor_note.content[:300]},
        )


def rebuild_timeline(db: Session, patient_id: uuid.UUID) -> None:
    db.query(TimelineEvent).filter(TimelineEvent.patient_id == patient_id).delete()
    visits = (
        db.query(Visit)
        .filter(Visit.patient_id == patient_id)
        .order_by(Visit.visit_date)
        .all()
    )
    for visit in visits:
        build_timeline_for_visit(db, patient_id, visit)
    db.commit()


def fetch_structured_summary(db: Session, patient_id: uuid.UUID) -> str:
    meds = (
        db.query(Medication)
        .join(Visit)
        .filter(Visit.patient_id == patient_id)
        .all()
    )
    labs = (
        db.query(LabResult)
        .join(Visit)
        .filter(Visit.patient_id == patient_id)
        .all()
    )
    allergies = db.query(Allergy).filter(Allergy.patient_id == patient_id).all()
    docs = (
        db.query(Document)
        .filter(Document.patient_id == patient_id)
        .order_by(Document.uploaded_at.desc())
        .limit(5)
        .all()
    )

    lines = ["=== Structured Patient Summary ==="]
    if allergies:
        lines.append("Allergies: " + ", ".join(a.allergen for a in allergies))
    if meds:
        lines.append("Medications:")
        for m in meds:
            lines.append(f"  - {m.name} {m.dose or ''} {m.frequency or ''}".strip())
    if labs:
        lines.append("Recent Labs:")
        for lab in labs[:10]:
            lines.append(f"  - {lab.test_name}: {lab.value} {lab.unit or ''}".strip())
    if docs:
        lines.append("Recent Documents:")
        for d in docs:
            lines.append(f"  - {d.doc_type}: {d.filename}")
    return "\n".join(lines)
