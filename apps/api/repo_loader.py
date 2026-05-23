import os
from urllib.parse import urlparse

import requests

GITHUB_API = "https://api.github.com"
GITHUB_RAW = "https://raw.githubusercontent.com"

ALLOWED_EXTENSIONS = {".md", ".py", ".ts", ".tsx", ".js", ".jsx", ".json"}
ALLOWED_FILENAMES = {"README", "readme"}
SKIP_PATH_PARTS = {
    "node_modules", ".next", ".git", "dist", "build", "out",
    "__pycache__", ".venv", "venv", ".pytest_cache", "coverage",
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
}
MAX_FILE_BYTES = 100_000  # ~100KB; bigger files are usually noise


def _headers() -> dict[str, str]:
    """Build auth headers if a GITHUB_TOKEN is set."""
    headers = {"Accept": "application/vnd.github+json"}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def parse_repo_url(url: str) -> tuple[str, str]:
    """Extract (owner, repo) from a GitHub URL."""
    parsed = urlparse(url.strip())

    if parsed.netloc not in ("github.com", "www.github.com"):
        raise ValueError(f"Not a GitHub URL: {url}")

    parts = parsed.path.strip("/").split("/")
    if len(parts) < 2:
        raise ValueError(f"URL is missing owner/repo: {url}")

    owner = parts[0]
    repo = parts[1].removesuffix(".git")
    return owner, repo


def get_default_branch(owner: str, repo: str) -> str:
    """Ask GitHub which branch is the default (main, master, etc.)."""
    r = requests.get(f"{GITHUB_API}/repos/{owner}/{repo}", headers=_headers(), timeout=10)
    r.raise_for_status()
    return r.json()["default_branch"]


def get_file_tree(owner: str, repo: str, branch: str) -> list[dict]:
    """Return the full recursive file tree for a branch.

    Each entry has: path, type ('blob' or 'tree'), size, sha.
    """
    url = f"{GITHUB_API}/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
    r = requests.get(url, headers=_headers(), timeout=10)
    r.raise_for_status()
    data = r.json()
    if data.get("truncated"):
        print("Warning: repo tree was truncated by GitHub (very large repo).")
    return data["tree"]


def filter_files(tree: list[dict]) -> list[dict]:
    """Keep only blob entries with useful extensions, dropping noise and huge files."""
    kept = []
    for entry in tree:
        if entry.get("type") != "blob":
            continue

        path = entry["path"]
        parts = path.split("/")

        if any(part in SKIP_PATH_PARTS for part in parts):
            continue

        filename = parts[-1]
        ext = "" if "." not in filename else "." + filename.rsplit(".", 1)[1].lower()

        if ext not in ALLOWED_EXTENSIONS and filename not in ALLOWED_FILENAMES:
            continue

        if entry.get("size", 0) > MAX_FILE_BYTES:
            continue

        kept.append(entry)
    return kept


def fetch_file_content(owner: str, repo: str, branch: str, path: str) -> str | None:
    """Fetch a single file's raw content. Returns None if it can't be decoded as text."""
    url = f"{GITHUB_RAW}/{owner}/{repo}/{branch}/{path}"
    r = requests.get(url, headers=_headers(), timeout=10)
    if r.status_code != 200:
        return None
    try:
        return r.content.decode("utf-8")
    except UnicodeDecodeError:
        return None


def load_repo_files(url: str) -> list[dict]:
    """End-to-end: URL in, list of {path, content} out."""
    owner, repo = parse_repo_url(url)
    branch = get_default_branch(owner, repo)
    tree = get_file_tree(owner, repo, branch)
    files = filter_files(tree)

    results = []
    for entry in files:
        content = fetch_file_content(owner, repo, branch, entry["path"])
        if content is None:
            continue
        results.append({"path": entry["path"], "content": content})
    return results