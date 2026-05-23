import anthropic

from embeddings import embed_texts, get_collection

TOP_K = 6
ANTHROPIC_MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 1024

_anthropic_client: anthropic.Anthropic | None = None


def _get_anthropic() -> anthropic.Anthropic:
    global _anthropic_client
    if _anthropic_client is None:
        _anthropic_client = anthropic.Anthropic()
    return _anthropic_client


SYSTEM_PROMPT = """You are an expert at explaining code repositories.
Answer the user's question using ONLY the provided repository excerpts.

Rules:
- Cite file paths inline like (src/foo.ts) when you reference them.
- If the excerpts don't contain enough information, say so clearly instead of guessing.
- Be concrete and concise. Prefer code references over generic prose."""


def retrieve(repo_id: str, question: str, k: int = TOP_K) -> list[dict]:
    """Return the top-k chunks most semantically similar to the question."""
    query_vector = embed_texts([question])[0]

    collection = get_collection()
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=k,
        where={"repo_id": repo_id},
    )

    ids = results["ids"][0]
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    return [
        {
            "id": ids[i],
            "text": documents[i],
            "metadata": metadatas[i],
            "distance": distances[i],
        }
        for i in range(len(ids))
    ]


def _build_user_message(question: str, chunks: list[dict]) -> str:
    excerpts = "\n\n".join(
        f"--- {c['metadata']['path']} (chunk {c['metadata']['chunk_index']}) ---\n{c['text']}"
        for c in chunks
    )
    return f"Repository excerpts:\n\n{excerpts}\n\n---\n\nQuestion: {question}"


def ask(repo_id: str, question: str) -> dict:
    """Run the full RAG pipeline: retrieve, prompt, generate. Returns answer + sources."""
    chunks = retrieve(repo_id, question)

    client = _get_anthropic()
    response = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=MAX_TOKENS,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": _build_user_message(question, chunks)},
        ],
    )

    answer = response.content[0].text
    return {
        "answer": answer,
        "sources": [
            {
                "path": c["metadata"]["path"],
                "chunk_index": c["metadata"]["chunk_index"],
                "distance": round(c["distance"], 3),
            }
            for c in chunks
        ],
    }
