"""Calls the LLM for classification + extraction, validates with Pydantic,
then maps the result onto ORM inserts (Visit, Medications, LabResults,
Allergies, DoctorNote) and rebuilds the patient's timeline."""
import uuid

from sqlalchemy.orm import Session

from app.ai import llm
from app.models.allergy import Allergy
from app.models.doctor_note import DoctorNote
from app.models.lab_result import LabResult
from app.models.medication import Medication
from app.models.visit import Visit
from app.schemas.document import ExtractedDocument
from app.services import timeline_service


def classify_and_extract(text: str) -> ExtractedDocument:
    doc_type_hint = llm.classify_document(text)
    extracted = llm.extract_entities(text, doc_type_hint=doc_type_hint)
    if extracted.doc_type == "Unknown" and doc_type_hint != "Unknown":
        extracted.doc_type = doc_type_hint
    return extracted


def persist_extracted(
    db: Session, patient_id: uuid.UUID, document_id: uuid.UUID, extracted: ExtractedDocument
) -> Visit:
    visit = Visit(
        patient_id=patient_id,
        document_id=document_id,
        visit_date=extracted.visit_date,
        doctor=extracted.doctor,
        hospital=extracted.hospital,
    )
    db.add(visit)
    db.flush()  # get visit.id without committing

    for med in extracted.medications:
        db.add(
            Medication(
                visit_id=visit.id,
                name=med.name,
                dose=med.dose,
                frequency=med.frequency,
                start_date=med.start_date,
                end_date=med.end_date,
            )
        )

    for lab in extracted.lab_results:
        db.add(
            LabResult(
                visit_id=visit.id,
                test_name=lab.test_name,
                value=lab.value,
                unit=lab.unit,
                reference_range=lab.reference_range,
                test_date=lab.test_date or extracted.visit_date,
            )
        )

    if extracted.doc_type == "DoctorNote" and extracted.doctor_note_content:
        db.add(DoctorNote(visit_id=visit.id, content=extracted.doctor_note_content))

    # Allergies are patient-level, not visit-level - only add ones we don't
    # already have on file (case-insensitive match on allergen name).
    existing = {a.allergen.lower() for a in db.query(Allergy).filter(Allergy.patient_id == patient_id)}
    for allergy in extracted.allergies:
        if allergy.allergen.lower() not in existing:
            db.add(Allergy(patient_id=patient_id, allergen=allergy.allergen, severity=allergy.severity))
            existing.add(allergy.allergen.lower())

    db.flush()
    db.refresh(visit)  # populate visit.medications / visit.lab_results / visit.doctor_note
    timeline_service.build_timeline_for_visit(db, patient_id, visit)

    db.commit()
    db.refresh(visit)
    return visit
