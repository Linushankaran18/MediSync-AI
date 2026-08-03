import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field


class MedicationEntity(BaseModel):
    name: str
    dose: str | None = None
    frequency: str | None = None
    start_date: date | None = None
    end_date: date | None = None


class LabResultEntity(BaseModel):
    test_name: str
    value: float | None = None
    unit: str | None = None
    reference_range: str | None = None
    test_date: date | None = None


class AllergyEntity(BaseModel):
    allergen: str
    severity: str | None = None


class ExtractedDocument(BaseModel):
    """Forced JSON output shape for the extraction LLM call."""

    doc_type: str = Field(description="One of: Prescription, LabReport, DoctorNote, DischargeSummary, Unknown")
    visit_date: date | None = None
    doctor: str | None = None
    hospital: str | None = None
    medications: list[MedicationEntity] = []
    lab_results: list[LabResultEntity] = []
    allergies: list[AllergyEntity] = []
    diagnoses: list[str] = []
    doctor_note_content: str | None = None
    notes_summary: str | None = None


class UploadResponse(BaseModel):
    message: str
    document_id: uuid.UUID
    doc_type: str
    ocr_quality: float
    alerts_triggered: list[str]


class DocumentOut(BaseModel):
    id: uuid.UUID
    filename: str
    doc_type: str | None
    ocr_quality: float | None
    uploaded_at: datetime

    class Config:
        from_attributes = True
