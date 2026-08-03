from pydantic import BaseModel


class SummaryResponse(BaseModel):
    document_count: int
    visit_count: int
    active_alerts: int
    medication_count: int
    lab_count: int
    recent_doc_type: str | None
