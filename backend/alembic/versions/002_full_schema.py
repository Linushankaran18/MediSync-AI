"""Complete the schema: documents, visits, medications, lab_results,
allergies, alerts, timeline_events, chat_history, doctor_notes.

001_initial.py only carried the Phase 1 foundation (users + patients); this
migration adds everything the rest of the application (models, report.py,
timeline_service.py) already depends on.

Revision ID: 002
Revises: 001
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("patients.id"), nullable=False),
        sa.Column("filename", sa.String(500), nullable=False),
        sa.Column("doc_type", sa.String(50), nullable=True),
        sa.Column("raw_text", sa.Text(), nullable=True),
        sa.Column("ocr_quality", sa.Float(), nullable=True),
        sa.Column("extracted_entities", postgresql.JSONB(), nullable=True),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_documents_patient_id", "documents", ["patient_id"])

    op.create_table(
        "visits",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("patients.id"), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("documents.id"), nullable=True),
        sa.Column("visit_date", sa.Date(), nullable=True),
        sa.Column("doctor", sa.String(255), nullable=True),
        sa.Column("hospital", sa.String(255), nullable=True),
    )
    op.create_index("ix_visits_patient_id", "visits", ["patient_id"])
    op.create_index("ix_visits_visit_date", "visits", ["visit_date"])

    op.create_table(
        "medications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("visit_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("visits.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("dose", sa.String(100), nullable=True),
        sa.Column("frequency", sa.String(100), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
    )
    op.create_index("ix_medications_visit_id", "medications", ["visit_id"])
    op.create_index("ix_medications_name", "medications", ["name"])

    op.create_table(
        "lab_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("visit_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("visits.id"), nullable=False),
        sa.Column("test_name", sa.String(255), nullable=False),
        sa.Column("value", sa.Float(), nullable=True),
        sa.Column("unit", sa.String(50), nullable=True),
        sa.Column("reference_range", sa.String(100), nullable=True),
        sa.Column("test_date", sa.Date(), nullable=True),
    )
    op.create_index("ix_lab_results_visit_id", "lab_results", ["visit_id"])
    op.create_index("ix_lab_results_test_name", "lab_results", ["test_name"])
    op.create_index("ix_lab_results_test_date", "lab_results", ["test_date"])

    op.create_table(
        "allergies",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("patients.id"), nullable=False),
        sa.Column("allergen", sa.String(255), nullable=False),
        sa.Column("severity", sa.String(50), nullable=True),
    )
    op.create_index("ix_allergies_patient_id", "allergies", ["patient_id"])
    op.create_index("ix_allergies_allergen", "allergies", ["allergen"])

    op.create_table(
        "doctor_notes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("visit_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("visits.id"), nullable=False, unique=True),
        sa.Column("content", sa.Text(), nullable=False),
    )

    op.create_table(
        "alerts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("patients.id"), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("documents.id"), nullable=True),
        sa.Column("alert_type", sa.String(50), nullable=False),
        sa.Column("severity", sa.String(20), nullable=False),
        sa.Column("details", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("resolved", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_alerts_patient_id", "alerts", ["patient_id"])
    op.create_index("ix_alerts_alert_type", "alerts", ["alert_type"])
    op.create_index("ix_alerts_severity", "alerts", ["severity"])
    op.create_index("ix_alerts_resolved", "alerts", ["resolved"])

    op.create_table(
        "timeline_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("patients.id"), nullable=False),
        sa.Column("visit_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("visits.id"), nullable=True),
        sa.Column("event_type", sa.String(50), nullable=False),
        sa.Column("event_date", sa.Date(), nullable=True),
        sa.Column("payload", postgresql.JSONB(), nullable=False, server_default="{}"),
    )
    op.create_index("ix_timeline_events_patient_id", "timeline_events", ["patient_id"])
    op.create_index("ix_timeline_events_event_date", "timeline_events", ["event_date"])

    op.create_table(
        "chat_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("patients.id"), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("evidence", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_chat_history_patient_id", "chat_history", ["patient_id"])


def downgrade() -> None:
    op.drop_table("chat_history")
    op.drop_table("timeline_events")
    op.drop_table("alerts")
    op.drop_table("doctor_notes")
    op.drop_table("allergies")
    op.drop_table("lab_results")
    op.drop_table("medications")
    op.drop_table("visits")
    op.drop_table("documents")
