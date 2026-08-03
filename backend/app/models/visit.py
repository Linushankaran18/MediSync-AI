import uuid
from datetime import date as date_type

from sqlalchemy import Date, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.postgres import Base
from app.models.base import gen_uuid


class Visit(Base):
    __tablename__ = "visits"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=gen_uuid)
    patient_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("patients.id"), index=True)
    document_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("documents.id"), nullable=True)
    visit_date: Mapped[date_type | None] = mapped_column(Date, nullable=True, index=True)
    doctor: Mapped[str | None] = mapped_column(String(255), nullable=True)
    hospital: Mapped[str | None] = mapped_column(String(255), nullable=True)

    patient: Mapped["Patient"] = relationship(back_populates="visits")
    document: Mapped["Document"] = relationship(back_populates="visit")
    medications: Mapped[list["Medication"]] = relationship(back_populates="visit")
    lab_results: Mapped[list["LabResult"]] = relationship(back_populates="visit")
    doctor_note: Mapped["DoctorNote"] = relationship(back_populates="visit", uselist=False)
