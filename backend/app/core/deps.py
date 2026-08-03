import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token, hash_password
from app.database.postgres import get_db
from app.models.patient import Patient
from app.models.user import User

# ============================================================================
# TEMP DEV BYPASS - set back to False to require real login again.
# While True, any request without a valid token is auto-logged-in as a fixed
# dev user (auto-created on first use) instead of getting a 401. Login/
# register still work normally; this only removes the requirement to use them.
# ============================================================================
DISABLE_AUTH_FOR_DEV = True
DEV_USER_EMAIL = "dev@local.test"
DEV_PATIENT_NAME = "Dev User"

# auto_error=False so a missing/malformed Authorization header returns None
# instead of raising, letting the dev-bypass branch below handle it.
bearer_scheme = HTTPBearer(auto_error=False)


def _get_or_create_dev_user(db: Session) -> User:
    user = db.query(User).filter(User.email == DEV_USER_EMAIL).first()
    if user:
        return user
    user = User(email=DEV_USER_EMAIL, password_hash=hash_password(uuid.uuid4().hex))
    db.add(user)
    db.flush()
    db.add(Patient(user_id=user.id, name=DEV_PATIENT_NAME))
    db.commit()
    db.refresh(user)
    return user


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        if DISABLE_AUTH_FOR_DEV:
            return _get_or_create_dev_user(db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    payload = decode_access_token(credentials.credentials)
    if not payload or "sub" not in payload:
        if DISABLE_AUTH_FOR_DEV:
            return _get_or_create_dev_user(db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    try:
        user_id = uuid.UUID(payload["sub"])
    except (ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def get_current_patient(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Patient:
    patient = db.query(Patient).filter(Patient.user_id == user.id).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No patient profile for this user")
    return patient
