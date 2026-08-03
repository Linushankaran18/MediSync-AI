"""LangChain chat-model abstraction: Ollama locally, Groq (or any
OpenAI-compatible cloud endpoint) in production, switched via LLM_PROVIDER.
Matches render.yaml (LLM_PROVIDER=cloud, Groq/llama-3.3-70b-versatile).

Structured extraction uses LangChain's with_structured_output (tool-calling
under the hood) rather than "please respond in JSON" - much lower failure
rate on malformed output, and works the same way regardless of provider.
"""
from functools import lru_cache

from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

from app.ai import prompts
from app.core.config import settings
from app.schemas.document import ExtractedDocument


@lru_cache
def get_llm():
    if settings.LLM_PROVIDER == "ollama":
        return ChatOllama(model=settings.OLLAMA_MODEL, base_url=settings.OLLAMA_BASE_URL, temperature=settings.LLM_TEMPERATURE)
    return ChatOpenAI(
        base_url=settings.CLOUD_LLM_URL,
        api_key=settings.CLOUD_LLM_API_KEY,
        model=settings.CLOUD_LLM_MODEL,
        temperature=settings.LLM_TEMPERATURE,
    )


def classify_document(text: str) -> str:
    chain = prompts.CLASSIFY_PROMPT | get_llm()
    result = chain.invoke({"document_text": text[:6000]})
    label = result.content.strip()
    valid = {"Prescription", "LabReport", "DoctorNote", "DischargeSummary", "Unknown"}
    return label if label in valid else "Unknown"


def extract_entities(text: str, doc_type_hint: str = "Unknown") -> ExtractedDocument:
    structured_llm = get_llm().with_structured_output(ExtractedDocument)
    chain = prompts.EXTRACT_PROMPT | structured_llm
    result = chain.invoke({"doc_type_hint": doc_type_hint, "document_text": text[:20000]})
    if isinstance(result, ExtractedDocument):
        return result
    return ExtractedDocument.model_validate(result)


def rag_answer(question: str, structured_context: str, retrieved_chunks: str) -> str:
    chain = prompts.RAG_PROMPT | get_llm()
    result = chain.invoke(
        {"structured_context": structured_context, "retrieved_chunks": retrieved_chunks, "question": question}
    )
    return result.content.strip()


def explain_alert(alert_type: str, severity: str, details: dict) -> str:
    chain = prompts.EXPLAIN_ALERT_PROMPT | get_llm()
    result = chain.invoke({"alert_type": alert_type, "severity": severity, "details": details})
    return result.content.strip()
