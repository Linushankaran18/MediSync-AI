"""Persistent local ChromaDB collection (embedded, no separate server
process). Collection is shared across patients; every read/write is scoped
with a `patient_id` metadata filter."""
from functools import lru_cache

import chromadb

from app.core.config import settings


@lru_cache
def get_chroma_client() -> chromadb.ClientAPI:
    return chromadb.PersistentClient(path=settings.CHROMA_PATH)


def get_collection():
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=settings.CHROMA_COLLECTION,
        metadata={"hnsw:space": "cosine"},
    )
