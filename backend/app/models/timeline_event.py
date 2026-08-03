import uuid
from datetime import date as date_type

from sqlalchemy import Date, ForeignKey, JSON, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.postgres import Base
from app.models.base import gen_uuid


class TimelineEvent(Base):
    __tablename__ = "timeline_events"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=gen_uuid)
    patient_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("patients.id"), index=True)
    visit_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("visits.id"), nullable=True)
    # visit | medication | lab_result | doctor_note
    event_type: Mapped[str] = mapped_column(String(50))
    event_date: Mapped[date_type | None] = mapped_column(Date, nullable=True, index=True)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)

    patient: Mapped["Patient"] = relationship(back_populates="timeline_events")
