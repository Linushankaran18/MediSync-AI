import uuid
from datetime import date as date_type

from sqlalchemy import Date, Float, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.postgres import Base
from app.models.base import gen_uuid


class LabResult(Base):
    __tablename__ = "lab_results"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=gen_uuid)
    visit_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("visits.id"), index=True)
    test_name: Mapped[str] = mapped_column(String(255), index=True)
    value: Mapped[float | None] = mapped_column(Float, nullable=True)
    unit: Mapped[str | None] = mapped_column(String(50), nullable=True)
    reference_range: Mapped[str | None] = mapped_column(String(100), nullable=True)
    test_date: Mapped[date_type | None] = mapped_column(Date, nullable=True, index=True)

    visit: Mapped["Visit"] = relationship(back_populates="lab_results")
