import uuid

from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str


class EvidenceItem(BaseModel):
    document_id: uuid.UUID | None
    snippet: str
    visit_date: str | None = None


class ChatResponse(BaseModel):
    answer: str
    evidence: list[EvidenceItem]
    confidence: int  # 0-100
    disclaimer: str
