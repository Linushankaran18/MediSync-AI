from datetime import date

from pydantic import BaseModel


class LabTrendPoint(BaseModel):
    date: date | None
    value: float
    unit: str | None = None


class LabTrendResponse(BaseModel):
    test_name: str
    trend: str  # increasing|decreasing|stable|insufficient_data
    points: list[LabTrendPoint]
