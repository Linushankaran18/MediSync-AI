"""Deterministic rule engine. No LLM decisions here - severity and the fact of
a match are decided purely in code. The LLM (ai.llm.explain_alert) only
explains an already-fired alert in plain language afterward, and is only
called on demand (not stored) since the frontend's Alert view doesn't surface
a cached explanation field.

Alert types match the frontend's AlertCard label map exactly: drug_interaction,
allergy, duplicate_prescription, dosage_conflict, lab_trend.

run_all_rules() re-evaluates a patient's active medications/allergies/labs on
every upload (a new document can retroactively create a conflict with
existing records). Each check is deduplicated against already-recorded alerts
of the same type using a signature (drug-name pair, or allergen+drug), not
row IDs, so re-running the engine on a later upload doesn't spam duplicate
rows for a fact already on file.
"""
import json
from datetime import date
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.models.allergy import Allergy
from app.models.lab_result import LabResult
from app.models.medication import Medication
from app.models.visit import Visit
from app.services.interaction_kb import ALLERGY_CROSS_REACTIVITY
from app.services.trend_service import compute_trend

_DATA_PATH = Path(__file__).parent / "data" / "drug_interactions.json"


def _load_drug_interactions() -> dict[frozenset, tuple[str, str]]:
    with open(_DATA_PATH) as f:
        rows = json.load(f)
    return {
        frozenset({row["drug_a"].lower(), row["drug_b"].lower()}): (row["severity"], row["description"])
        for row in rows
    }


DRUG_INTERACTIONS = _load_drug_interactions()


def _active_medications(db: Session, patient_id) -> list[Medication]:
    return (
        db.query(Medication)
        .join(Visit, Medication.visit_id == Visit.id)
        .filter(Visit.patient_id == patient_id)
        .all()
    )


def _ranges_overlap(a_start, a_end, b_start, b_end) -> bool:
    a_end = a_end or date.max
    b_end = b_end or date.max
    a_start = a_start or date.min
    b_start = b_start or date.min
    return a_start <= b_end and b_start <= a_end


def _existing_signatures(db: Session, patient_id, alert_type: str) -> set[tuple]:
    existing = db.query(Alert).filter(Alert.patient_id == patient_id, Alert.alert_type == alert_type).all()
    sigs = set()
    for a in existing:
        d = a.details or {}
        if alert_type == "drug_interaction":
            sigs.add(frozenset({d.get("medication_a", "").lower(), d.get("medication_b", "").lower()}))
        elif alert_type == "allergy":
            sigs.add((d.get("allergen", "").lower(), d.get("medication", "").lower()))
        elif alert_type in ("duplicate_prescription", "dosage_conflict"):
            sigs.add((d.get("medication", "").lower(), d.get("dose_a"), d.get("dose_b")))
        elif alert_type == "lab_trend":
            sigs.add((d.get("test_name", "").lower(), d.get("trend")))
    return sigs


def check_drug_interactions(db: Session, patient_id, document_id) -> list[Alert]:
    meds = _active_medications(db, patient_id)
    alerts: list[Alert] = []
    seen = _existing_signatures(db, patient_id, "drug_interaction")
    seen_this_run: set[frozenset] = set()

    for i, med_a in enumerate(meds):
        for med_b in meds[i + 1 :]:
            name_a, name_b = med_a.name.lower().strip(), med_b.name.lower().strip()
            if name_a == name_b:
                continue
            for kb_pair, (severity, description) in DRUG_INTERACTIONS.items():
                d1, d2 = tuple(kb_pair)
                if not ((d1 in name_a and d2 in name_b) or (d1 in name_b and d2 in name_a)):
                    continue
                sig = frozenset({name_a, name_b})
                if sig in seen or sig in seen_this_run:
                    continue
                seen_this_run.add(sig)
                alerts.append(
                    Alert(
                        patient_id=patient_id,
                        document_id=document_id,
                        alert_type="drug_interaction",
                        severity=severity,
                        details={"medication_a": med_a.name, "medication_b": med_b.name, "description": description},
                    )
                )
    return alerts


def check_allergy_conflicts(db: Session, patient_id, document_id) -> list[Alert]:
    meds = _active_medications(db, patient_id)
    allergies = db.query(Allergy).filter(Allergy.patient_id == patient_id).all()
    alerts: list[Alert] = []
    seen = _existing_signatures(db, patient_id, "allergy")
    seen_this_run: set[tuple] = set()

    for allergy in allergies:
        allergen_key = allergy.allergen.lower().strip()
        cross_reactive_terms = ALLERGY_CROSS_REACTIVITY.get(allergen_key, [allergen_key])
        for med in meds:
            med_name = med.name.lower().strip()
            if not (any(term in med_name for term in cross_reactive_terms) or allergen_key in med_name):
                continue
            sig = (allergen_key, med_name)
            if sig in seen or sig in seen_this_run:
                continue
            seen_this_run.add(sig)
            alerts.append(
                Alert(
                    patient_id=patient_id,
                    document_id=document_id,
                    alert_type="allergy",
                    severity=allergy.severity or "critical",
                    details={
                        "allergen": allergy.allergen,
                        "medication": med.name,
                        "description": f"Patient has a documented {allergy.allergen} allergy; {med.name} may cross-react.",
                    },
                )
            )
    return alerts


def check_duplicate_and_dosage(db: Session, patient_id, document_id) -> list[Alert]:
    meds = _active_medications(db, patient_id)
    alerts: list[Alert] = []
    seen_dup = _existing_signatures(db, patient_id, "duplicate_prescription")
    seen_dosage = _existing_signatures(db, patient_id, "dosage_conflict")
    seen_this_run: set[tuple] = set()

    for i, med_a in enumerate(meds):
        for med_b in meds[i + 1 :]:
            name = med_a.name.lower().strip()
            if name != med_b.name.lower().strip():
                continue
            if not _ranges_overlap(med_a.start_date, med_a.end_date, med_b.start_date, med_b.end_date):
                continue

            dose_a, dose_b = (med_a.dose or "").strip().lower(), (med_b.dose or "").strip().lower()
            is_duplicate = dose_a == dose_b
            alert_type = "duplicate_prescription" if is_duplicate else "dosage_conflict"
            sig = (name, None, None) if is_duplicate else (name, dose_a, dose_b)
            already_seen = seen_dup if is_duplicate else seen_dosage

            if sig in already_seen or sig in seen_this_run:
                continue
            seen_this_run.add(sig)

            if is_duplicate:
                alerts.append(
                    Alert(
                        patient_id=patient_id,
                        document_id=document_id,
                        alert_type="duplicate_prescription",
                        severity="warning",
                        details={"medication": med_a.name, "description": "Same medication prescribed twice with overlapping active dates."},
                    )
                )
            else:
                alerts.append(
                    Alert(
                        patient_id=patient_id,
                        document_id=document_id,
                        alert_type="dosage_conflict",
                        severity="warning",
                        details={
                            "medication": med_a.name,
                            "dose_a": med_a.dose,
                            "dose_b": med_b.dose,
                            "description": "Same medication prescribed at different doses in overlapping windows.",
                        },
                    )
                )
    return alerts


def check_lab_trends(db: Session, patient_id, document_id) -> list[Alert]:
    test_names = {
        row[0]
        for row in db.query(LabResult.test_name).join(Visit, LabResult.visit_id == Visit.id).filter(Visit.patient_id == patient_id).distinct()
    }
    alerts: list[Alert] = []
    seen = _existing_signatures(db, patient_id, "lab_trend")
    seen_this_run: set[tuple] = set()

    for test_name in test_names:
        rows = (
            db.query(LabResult)
            .join(Visit, LabResult.visit_id == Visit.id)
            .filter(Visit.patient_id == patient_id, LabResult.test_name == test_name)
            .filter(LabResult.test_date.isnot(None), LabResult.value.isnot(None))
            .order_by(LabResult.test_date.asc())
            .all()
        )
        if len(rows) < 3:
            continue
        trend = compute_trend([(r.test_date, r.value) for r in rows])
        if trend not in ("increasing", "decreasing"):
            continue
        sig = (test_name.lower(), trend)
        if sig in seen or sig in seen_this_run:
            continue
        seen_this_run.add(sig)
        alerts.append(
            Alert(
                patient_id=patient_id,
                document_id=document_id,
                alert_type="lab_trend",
                severity="warning",
                details={
                    "test_name": test_name,
                    "trend": trend,
                    "description": f"{test_name} has been {trend} over the last {len(rows)} results.",
                },
            )
        )
    return alerts


def run_all_rules(db: Session, patient_id, document_id=None) -> list[Alert]:
    alerts = (
        check_drug_interactions(db, patient_id, document_id)
        + check_allergy_conflicts(db, patient_id, document_id)
        + check_duplicate_and_dosage(db, patient_id, document_id)
        + check_lab_trends(db, patient_id, document_id)
    )
    for alert in alerts:
        db.add(alert)
    db.commit()
    for alert in alerts:
        db.refresh(alert)
    return alerts
