from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from requests import HTTPError

from chunker import chunk_files
from embeddings import store_chunks
from rag import ask
from repo_loader import load_repo_files, parse_repo_url

load_dotenv()

app = FastAPI(title="RepoChat AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class IndexRepoRequest(BaseModel):
    repo_url: str


class AskRequest(BaseModel):
    repo_id: str
    question: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/index-repo")
def index_repo(req: IndexRepoRequest):
    try:
        owner, repo = parse_repo_url(req.repo_url)
        files = load_repo_files(req.repo_url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPError as e:
        raise HTTPException(status_code=502, detail=f"GitHub API error: {e}")

    repo_id = f"{owner}/{repo}"
    chunks = chunk_files(files, repo_id=repo_id)
    stored = store_chunks(chunks)

    return {
        "repo_id": repo_id,
        "file_count": len(files),
        "chunk_count": stored,
    }


@app.post("/ask")
def ask_question(req: AskRequest):
    question = req.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="question must not be empty")

    result = ask(req.repo_id, question)

    if not result["sources"]:
        raise HTTPException(
            status_code=404,
            detail=f"No indexed content found for repo_id '{req.repo_id}'. Index it first via /index-repo.",
        )

    return result
