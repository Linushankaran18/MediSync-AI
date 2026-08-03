"""LangChain-based chunking for the RAG ingestion path."""
from langchain_text_splitters import RecursiveCharacterTextSplitter

_splitter = RecursiveCharacterTextSplitter(chunk_size=512 * 4, chunk_overlap=64 * 4)


def chunk_text(text: str) -> list[str]:
    if not text or not text.strip():
        return []
    return _splitter.split_text(text)
