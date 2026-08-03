import uuid

from sqlalchemy import ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.postgres import Base
from app.models.base import gen_uuid


class Allergy(Base):
    __tablename__ = "allergies"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=gen_uuid)
    patient_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("patients.id"), index=True)
    allergen: Mapped[str] = mapped_column(String(255), index=True)
    severity: Mapped[str | None] = mapped_column(String(50), nullable=True)

    patient: Mapped["Patient"] = relationship(back_populates="allergies")
