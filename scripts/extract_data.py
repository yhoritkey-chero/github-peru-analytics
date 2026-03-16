import os
import json
import logging
from loguru import logger
from src.extraction.github_client import GitHubClient
from src.extraction.user_extractor import UserExtractor
from src.extraction.repo_extractor import RepoExtractor

def main():
    logger.add("data/raw/extraction.log", rotation="500 MB")
    logger.info("Starting data extraction for GitHub Peru Analytics")
    
    # Ensure directories exist
    os.makedirs("data/raw/users", exist_ok=True)
    os.makedirs("data/raw/repos", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)

    client = GitHubClient()
    user_extractor = UserExtractor(client)
    repo_extractor = RepoExtractor(client)

    logger.info("Searching for users in Peru...")
    # Using 'Peru' as the primary location
    users = user_extractor.search_users_by_location("Peru", max_users=1000) # testing with 200 first, target is 1000 repos total.
    
    logger.info(f"Found {len(users)} users. Saving to raw data...")
    with open("data/raw/users/peru_users.json", "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)

    all_repos = []
    usernames = [u["login"] for u in users]
    
    logger.info("Fetching repositories for users...")
    repos = repo_extractor.search_repos_by_stars(usernames, min_stars=0)
    
    logger.info(f"Found {len(repos)} repositories in total. Saving to raw data...")
    with open("data/raw/repos/peru_repos.json", "w", encoding="utf-8") as f:
        json.dump(repos, f, indent=2)

    logger.info("Extraction complete!")

if __name__ == "__main__":
    main()
