import uuid
from datetime import date

from pydantic import BaseModel


class TimelineEventOut(BaseModel):
    id: uuid.UUID
    event_type: str
    event_date: date | None
    payload: dict | None
    visit_id: uuid.UUID | None

    class Config:
        from_attributes = True
