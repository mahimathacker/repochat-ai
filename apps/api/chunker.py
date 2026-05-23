from langchain_text_splitters import Language, RecursiveCharacterTextSplitter

EXT_TO_LANGUAGE = {
    ".py": Language.PYTHON,
    ".ts": Language.TS,
    ".tsx": Language.TS,
    ".js": Language.JS,
    ".jsx": Language.JS,
    ".md": Language.MARKDOWN,
}

CHUNK_SIZE = 1500
CHUNK_OVERLAP = 200


def _splitter_for(path: str) -> RecursiveCharacterTextSplitter:
    """Pick a language-aware splitter for the file, or a generic one."""
    ext = "." + path.rsplit(".", 1)[1].lower() if "." in path else ""
    if ext in EXT_TO_LANGUAGE:
        return RecursiveCharacterTextSplitter.from_language(
            language=EXT_TO_LANGUAGE[ext],
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        )
    return RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )


def chunk_files(files: list[dict], repo_id: str) -> list[dict]:
    """Split files into chunks. Returns [{id, text, metadata}, ...]."""
    chunks = []
    for f in files:
        splitter = _splitter_for(f["path"])
        pieces = splitter.split_text(f["content"])
        for i, text in enumerate(pieces):
            chunks.append({
                "id": f"{repo_id}::{f['path']}::{i}",
                "text": text,
                "metadata": {
                    "repo_id": repo_id,
                    "path": f["path"],
                    "chunk_index": i,
                },
            })
    return chunks
