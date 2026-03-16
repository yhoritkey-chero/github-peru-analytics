from .github_client import GitHubClient
import base64

class RepoExtractor:
    def __init__(self, client: GitHubClient):
        self.client = client

    def search_repos_by_stars(self, location_users: list[str], min_stars: int = 1) -> list[dict]:
        """Search for top repositories from users in a location."""
        repos = []
        for username in location_users:
            try:
                user_repos = self.client.make_request(
                    f"users/{username}/repos",
                    params={"sort": "stars", "direction": "desc"}
                )
                for repo in user_repos:
                    # Ignore None stargazers_count
                    if repo.get("stargazers_count", 0) >= min_stars:
                        repos.append(repo)
            except Exception:
                continue

        # Sort all repos by stars and take top 1000
        repos.sort(key=lambda x: x.get("stargazers_count", 0), reverse=True)
        return repos[:1000]

    def get_repo_readme(self, owner: str, repo: str) -> str:
        """Get the README content of a repository."""
        try:
            result = self.client.make_request(f"repos/{owner}/{repo}/readme")
            content = base64.b64decode(result["content"]).decode("utf-8", errors="ignore")
            return content[:5000]
        except Exception:
            return ""

    def get_repo_languages(self, owner: str, repo: str) -> dict:
        """Get the language breakdown of a repository."""
        try:
            return self.client.make_request(f"repos/{owner}/{repo}/languages")
        except Exception:
            return {}
