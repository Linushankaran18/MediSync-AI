"""Deleting a document has to unwind everything that upload.py/parser_service
built on top of it: the Visit it produced (and that visit's medications, lab
results, doctor note), any Alerts raised against it, its TimelineEvents, its
Chroma embeddings, and the file on disk. None of the FK columns involved are
declared ON DELETE CASCADE, so this is done manually, children-first, to
avoid FK violations.

Allergies are intentionally left alone: they're patient-level (not tied to a
single document/visit - see parser_service.persist_extracted), and multiple
documents can contribute to or corroborate the same allergen, so there's no
single document whose deletion should retract a patient's allergy record.
"""
import logging
import os
import uuid

from sqlalchemy.orm import Session

from app.models import Alert, Document, LabResult, Medication, TimelineEvent, Visit
from app.models.doctor_note import DoctorNote
from app.services import embedding_service

logger = logging.getLogger(__name__)


def delete_document(db: Session, document: Document) -> None:
    visit = db.query(Visit).filter(Visit.document_id == document.id).first()
    if visit:
        db.query(TimelineEvent).filter(TimelineEvent.visit_id == visit.id).delete()
        db.query(Medication).filter(Medication.visit_id == visit.id).delete()
        db.query(LabResult).filter(LabResult.visit_id == visit.id).delete()
        db.query(DoctorNote).filter(DoctorNote.visit_id == visit.id).delete()
        db.delete(visit)

    db.query(Alert).filter(Alert.document_id == document.id).delete()

    document_id = document.id
    file_path = document.file_path
    db.delete(document)
    db.commit()

    # Best-effort cleanup of external state - a failure here shouldn't leave
    # the DB row un-deleted or roll back the transaction above, but it is
    # logged so orphaned embeddings/files can be spotted.
    try:
        embedding_service.delete_document_embeddings(document_id)
    except Exception:
        logger.exception("Failed to delete Chroma embeddings for document %s", document_id)

    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
        except OSError:
            logger.exception("Failed to remove stored file %s for document %s", file_path, document_id)
