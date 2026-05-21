# RepoChat AI

AI explains any codebase.

RepoChat AI lets you paste a public GitHub repository URL and ask questions about the codebase using AI-powered retrieval and semantic search.

It is built to help developers quickly understand unfamiliar repositories, architecture, APIs, and project structure.

## Features

- Paste any public GitHub repository URL
- Automatically fetch and process repository files
- Chunk and embed code and documentation
- Ask natural-language questions about the repo
- Get AI-generated answers with source references
- Use a simple developer-focused UI

## Example Questions

- What does this project do?
- Explain the architecture.
- How is authentication implemented?
- Where is database logic handled?
- How do I run this locally?
- Which APIs are exposed?

## Tech Stack

### Frontend

- Next.js
- React
- Tailwind CSS
- TypeScript

### Backend

- FastAPI
- LangChain
- OpenAI / Claude API
- ChromaDB
- GitHub API

## Folder Structure

```text
repochat-ai/
  apps/
    web/
    api/

  data/
    chroma/

  README.md
```

## How It Works

1. User pastes a GitHub repository URL.
2. Backend fetches repository files.
3. Files are chunked and embedded.
4. Embeddings are stored in ChromaDB.
5. User asks questions about the repository.
6. Relevant chunks are retrieved.
7. AI generates an answer with source references.

## API Endpoints

### Index Repository

```http
POST /index-repo
```

Input:

```json
{
  "repo_url": "https://github.com/owner/repo"
}
```

### Ask Questions

```http
POST /ask
```

Input:

```json
{
  "repo_id": "repo-name",
  "question": "How does authentication work?"
}
```

## Local Development

### Frontend

```bash
cd apps/web
npm install
npm run dev
```

The frontend runs locally with the Next.js development server.

### Backend

```bash
cd apps/api
pip install -r requirements.txt
uvicorn main:app --reload
```

The backend runs locally with FastAPI and serves the indexing and question-answering endpoints.

## Environment Variables

Create an environment file for the backend and add the API keys needed by the services you use:

```env
OPENAI_API_KEY=
GITHUB_TOKEN=
```

## Future Improvements

- Support large repositories
- Repo architecture visualization
- Multi-repo chat
- Code dependency graphs
- MCP integration
- Streaming responses
- Memory and session support

## Why I Built This

Developers spend too much time understanding unfamiliar codebases.

RepoChat AI is an experiment in combining RAG, semantic search, code understanding, and AI-assisted developer workflows to make onboarding into repositories much faster.
