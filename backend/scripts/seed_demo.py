"""Seed demo account and sample medical data for MediSync AI."""

import uuid
from datetime import date, datetime, timezone

from app.core.security import hash_password
from app.database.postgres import SessionLocal
from app.models import (
    Alert,
    Allergy,
    Document,
    LabResult,
    Medication,
    Patient,
    TimelineEvent,
    User,
    Visit,
)


def seed():
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == "demo@medisync.ai").first()
        if existing:
            print("Demo account already exists. Skipping seed.")
            return

        user = User(
            id=uuid.uuid4(),
            email="demo@medisync.ai",
            password_hash=hash_password("demo1234"),
        )
        db.add(user)
        db.flush()

        patient = Patient(
            id=uuid.uuid4(),
            user_id=user.id,
            name="John Demo",
            dob=date(1985, 3, 15),
        )
        db.add(patient)
        db.flush()

        # Visit 1 - Prescription with penicillin allergy conflict
        doc1 = Document(
            id=uuid.uuid4(),
            patient_id=patient.id,
            filename="Prescription.pdf",
            doc_type="Prescription",
            raw_text="Prescription\nDr. Silva\nDate: 2025-04-01\nAmoxicillin 500mg twice daily\nMetformin 500mg once daily",
            ocr_quality=0.92,
            extracted_entities={"type": "Prescription", "doctor": "Dr. Silva"},
        )
        db.add(doc1)
        db.flush()

        visit1 = Visit(
            id=uuid.uuid4(),
            patient_id=patient.id,
            document_id=doc1.id,
            visit_date=date(2025, 4, 1),
            doctor="Dr. Silva",
            hospital="City General Hospital",
        )
        db.add(visit1)
        db.flush()

        db.add(Allergy(patient_id=patient.id, allergen="Penicillin", severity="critical"))
        db.add(Medication(visit_id=visit1.id, name="Amoxicillin", dose="500mg", frequency="twice daily"))
        db.add(Medication(visit_id=visit1.id, name="Metformin", dose="500mg", frequency="once daily"))

        # Visit 2 - Lab report
        doc2 = Document(
            id=uuid.uuid4(),
            patient_id=patient.id,
            filename="LabReport.pdf",
            doc_type="LabReport",
            raw_text="Lab Results\nBlood Sugar: 145 mg/dL\nCholesterol: 220 mg/dL\nCreatinine: 1.1 mg/dL",
            ocr_quality=0.88,
            extracted_entities={"type": "LabReport"},
        )
        db.add(doc2)
        db.flush()

        visit2 = Visit(
            id=uuid.uuid4(),
            patient_id=patient.id,
            document_id=doc2.id,
            visit_date=date(2025, 5, 15),
            doctor="Dr. Silva",
            hospital="City General Hospital",
        )
        db.add(visit2)
        db.flush()

        db.add(LabResult(visit_id=visit2.id, test_name="Blood Sugar", value=145, unit="mg/dL", test_date=date(2025, 5, 15)))
        db.add(LabResult(visit_id=visit2.id, test_name="Cholesterol", value=220, unit="mg/dL", test_date=date(2025, 5, 15)))
        db.add(LabResult(visit_id=visit2.id, test_name="Creatinine", value=1.1, unit="mg/dL", test_date=date(2025, 5, 15)))

        # Visit 3 - More labs showing trend
        doc3 = Document(
            id=uuid.uuid4(),
            patient_id=patient.id,
            filename="LabReport2.pdf",
            doc_type="LabReport",
            raw_text="Follow-up Labs\nBlood Sugar: 170 mg/dL\nBlood Sugar fasting: 170",
            ocr_quality=0.90,
            extracted_entities={"type": "LabReport"},
        )
        db.add(doc3)
        db.flush()

        visit3 = Visit(
            id=uuid.uuid4(),
            patient_id=patient.id,
            document_id=doc3.id,
            visit_date=date(2025, 7, 20),
            doctor="Dr. Silva",
            hospital="City General Hospital",
        )
        db.add(visit3)
        db.flush()

        db.add(LabResult(visit_id=visit3.id, test_name="Blood Sugar", value=170, unit="mg/dL", test_date=date(2025, 7, 20)))

        # Earlier lab for trend
        visit0 = Visit(
            id=uuid.uuid4(),
            patient_id=patient.id,
            visit_date=date(2025, 2, 10),
            doctor="Dr. Silva",
            hospital="City General Hospital",
        )
        db.add(visit0)
        db.flush()
        db.add(LabResult(visit_id=visit0.id, test_name="Blood Sugar", value=120, unit="mg/dL", test_date=date(2025, 2, 10)))

        # Timeline events
        for visit, etype, payload in [
            (visit1, "visit", {"doctor": "Dr. Silva", "hospital": "City General Hospital"}),
            (visit1, "medication", {"name": "Amoxicillin", "dose": "500mg"}),
            (visit1, "medication", {"name": "Metformin", "dose": "500mg"}),
            (visit2, "visit", {"doctor": "Dr. Silva"}),
            (visit2, "lab_result", {"test_name": "Blood Sugar", "value": 145}),
            (visit3, "lab_result", {"test_name": "Blood Sugar", "value": 170}),
        ]:
            db.add(
                TimelineEvent(
                    patient_id=patient.id,
                    visit_id=visit.id,
                    event_type=etype,
                    event_date=visit.visit_date,
                    payload=payload,
                )
            )

        # Pre-seed critical allergy alert
        db.add(
            Alert(
                patient_id=patient.id,
                alert_type="allergy",
                severity="critical",
                details={
                    "allergen": "Penicillin",
                    "medication": "Amoxicillin",
                    "dose": "500mg",
                },
            )
        )

        db.commit()
        print("Demo account seeded: demo@medisync.ai / demo1234")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
