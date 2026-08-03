import uuid

from sqlalchemy import ForeignKey, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.postgres import Base
from app.models.base import gen_uuid


class DoctorNote(Base):
    """One-to-one with Visit. Populated when an uploaded document classifies
    as a DoctorNote — free-text clinical note content, surfaced on the
    timeline as a 'doctor_note' event."""

    __tablename__ = "doctor_notes"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=gen_uuid)
    visit_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("visits.id"), unique=True)
    content: Mapped[str] = mapped_column(Text)

    visit: Mapped["Visit"] = relationship(back_populates="doctor_note")
