const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type IndexRepoResponse = {
  repo_id: string;
  file_count: number;
  chunk_count: number;
};

export type Source = {
  path: string;
  chunk_index: number;
  distance: number;
};

export type AskResponse = {
  answer: string;
  sources: Source[];
};

async function postJson<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`${res.status}: ${detail || res.statusText}`);
  }

  return res.json() as Promise<T>;
}

export function indexRepo(repoUrl: string) {
  return postJson<IndexRepoResponse>("/index-repo", { repo_url: repoUrl });
}

export function ask(repoId: string, question: string) {
  return postJson<AskResponse>("/ask", { repo_id: repoId, question });
}
