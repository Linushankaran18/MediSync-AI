from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.database.postgres import get_db
from app.models.patient import Patient
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user = User(email=payload.email, password_hash=hash_password(payload.password))
    db.add(user)
    db.flush()

    patient = Patient(user_id=user.id, name=payload.name)
    db.add(patient)
    db.commit()
    db.refresh(patient)

    token = create_access_token(subject=user.id)
    return TokenResponse(access_token=token, patient_id=patient.id, patient_name=patient.name)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    patient = db.query(Patient).filter(Patient.user_id == user.id).first()
    token = create_access_token(subject=user.id)
    return TokenResponse(access_token=token, patient_id=patient.id, patient_name=patient.name)
