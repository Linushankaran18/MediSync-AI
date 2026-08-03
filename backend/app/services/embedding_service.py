"""Local, free, offline embeddings (bge-small-en-v1.5 via sentence-transformers)
plus the read/write paths against the ChromaDB collection."""
from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.ai.chunker import chunk_text
from app.core.config import settings
from app.database.chromadb import get_collection


@lru_cache
def _get_model() -> SentenceTransformer:
    return SentenceTransformer(settings.EMBEDDING_MODEL)


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    model = _get_model()
    # bge models recommend a query instruction prefix for asymmetric search;
    # passages are embedded as-is.
    return model.encode(texts, normalize_embeddings=True).tolist()


def embed_query(query: str) -> list[float]:
    model = _get_model()
    instructed = f"Represent this sentence for searching relevant passages: {query}"
    return model.encode([instructed], normalize_embeddings=True).tolist()[0]


def ingest_document(patient_id, document_id, doc_type: str | None, visit_date, raw_text: str) -> int:
    """Chunk + embed + upsert a document's text into Chroma. Returns chunk count.
    patient_id/document_id may be UUID objects - Chroma metadata only accepts
    str/int/float/bool, so they're stringified here."""
    chunks = chunk_text(raw_text)
    if not chunks:
        return 0

    patient_id, document_id = str(patient_id), str(document_id)
    embeddings = embed_texts(chunks)
    ids = [f"{document_id}:{i}" for i in range(len(chunks))]
    metadatas = [
        {
            "patient_id": patient_id,
            "document_id": document_id,
            "doc_type": doc_type or "Unknown",
            "visit_date": str(visit_date) if visit_date else "",
            "chunk_index": i,
        }
        for i in range(len(chunks))
    ]

    collection = get_collection()
    collection.upsert(ids=ids, embeddings=embeddings, documents=chunks, metadatas=metadatas)
    return len(chunks)


def query_patient_documents(patient_id, question: str, n_results: int = 5) -> list[dict]:
    collection = get_collection()
    query_embedding = embed_query(question)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where={"patient_id": str(patient_id)},
    )

    hits = []
    ids = results.get("ids", [[]])[0]
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    dists = results.get("distances", [[]])[0]
    for i in range(len(ids)):
        hits.append(
            {
                "id": ids[i],
                "text": docs[i],
                "metadata": metas[i],
                "distance": dists[i],
                # cosine distance -> similarity in [0,1] (clamped)
                "similarity": max(0.0, 1.0 - dists[i] / 2.0),
            }
        )
    return hits
