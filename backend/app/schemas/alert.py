import uuid
from datetime import datetime

from pydantic import BaseModel


class AlertOut(BaseModel):
    id: uuid.UUID
    alert_type: str
    severity: str
    details: dict
    resolved: bool
    created_at: datetime

    class Config:
        from_attributes = True
