import os
import requests
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()

class GitHubClient:
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.token}" if self.token else "",
            "Accept": "application/vnd.github.v3+json"
        }

    def check_rate_limit(self) -> dict:
        """Check current rate limit status."""
        response = requests.get(
            f"{self.base_url}/rate_limit",
            headers=self.headers
        )
        return response.json()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=60)
    )
    def make_request(self, endpoint: str, params: dict = None) -> dict:
        """Make a rate-limit-aware request to GitHub API."""
        response = requests.get(
            f"{self.base_url}/{endpoint}",
            headers=self.headers,
            params=params
        )
        # Check rate limit
        remaining = int(response.headers.get("X-RateLimit-Remaining", 0))
        if remaining < 10:
            reset_time = int(response.headers.get("X-RateLimit-Reset", 0))
            # Handled by tenacity and exponential backoff generally, but can add explicit sleep if needed
            
        response.raise_for_status()
        return response.json()
