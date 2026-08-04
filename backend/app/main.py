from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import alerts, auth, chat, documents, report, timeline, upload
from app.core.config import settings

app = FastAPI(title="MediSync AI", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(upload.router)
app.include_router(documents.router)
app.include_router(timeline.router)
app.include_router(alerts.router)
app.include_router(chat.router)
app.include_router(report.router)


@app.get("/health")
def health():
    return {"status": "ok"}
