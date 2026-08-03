from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_patient
from app.database.postgres import get_db
from app.models.patient import Patient
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.rag_service import answer_question

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    patient: Patient = Depends(get_current_patient),
    db: Session = Depends(get_db),
):
    result = answer_question(db, patient.id, payload.question)
    return ChatResponse(**result)
