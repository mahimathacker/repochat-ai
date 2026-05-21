from urllib.parse import urlparse


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
