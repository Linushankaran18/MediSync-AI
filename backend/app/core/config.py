from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database (Postgres in prod/Docker; sqlite is only used for local
    # unit-testing convenience since the Uuid column type is portable)
    DATABASE_URL: str = "postgresql://medisync:medisync@localhost:5432/medisync"

    # Auth
    JWT_SECRET: str = "dev-secret-change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440

    # LLM: Ollama locally, Groq (or any OpenAI-compatible cloud endpoint) in
    # production. Matches render.yaml (LLM_PROVIDER=cloud, Groq).
    LLM_PROVIDER: str = "ollama"  # "ollama" | "cloud"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen3:8b"
    CLOUD_LLM_URL: str = "https://api.groq.com/openai/v1"
    CLOUD_LLM_API_KEY: str = ""
    CLOUD_LLM_MODEL: str = "llama-3.3-70b-versatile"
    LLM_TEMPERATURE: float = 0.0

    # Vision OCR: uploaded images/scanned PDFs (no real text layer) go
    # through Gemini, which transcribes the image directly - handles
    # handwriting and mixed-language text far better than pypdf/pdfplumber
    # or classic OCR.
    GEMINI_API_KEY: str = ""
    GEMINI_VISION_MODEL: str = "gemini-3.6-flash"

    # Embeddings / vector store
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
    CHROMA_PATH: str = "./chroma_data"
    CHROMA_COLLECTION: str = "patient_documents"

    # Storage
    UPLOAD_DIR: str = "./uploads"

    # CORS
    FRONTEND_ORIGIN: str = "http://localhost:5173"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
