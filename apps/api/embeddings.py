from pathlib import Path

import chromadb
from openai import OpenAI

OPENAI_EMBED_MODEL = "text-embedding-3-small"
COLLECTION_NAME = "repos"
CHROMA_PATH = str(Path(__file__).resolve().parent.parent.parent / "data" / "chroma")
EMBED_BATCH = 100

_openai_client: OpenAI | None = None
_collection = None


def _get_openai() -> OpenAI:
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAI()
    return _openai_client


def get_collection():
    """Return a persistent Chroma collection (creating it if needed)."""
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        _collection = client.get_or_create_collection(COLLECTION_NAME)
    return _collection


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Turn a list of strings into a list of embedding vectors."""
    client = _get_openai()
    vectors: list[list[float]] = []
    for i in range(0, len(texts), EMBED_BATCH):
        batch = texts[i:i + EMBED_BATCH]
        resp = client.embeddings.create(model=OPENAI_EMBED_MODEL, input=batch)
        vectors.extend(d.embedding for d in resp.data)
    return vectors


def store_chunks(chunks: list[dict]) -> int:
    """Embed and upsert chunks into ChromaDB. Returns the count stored."""
    if not chunks:
        return 0

    texts = [c["text"] for c in chunks]
    vectors = embed_texts(texts)

    collection = get_collection()
    collection.upsert(
        ids=[c["id"] for c in chunks],
        embeddings=vectors,
        documents=texts,
        metadatas=[c["metadata"] for c in chunks],
    )
    return len(chunks)
