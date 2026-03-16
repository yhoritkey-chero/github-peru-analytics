import os
import json
import pandas as pd
from loguru import logger
from src.metrics.user_metrics import UserMetricsCalculator

def main():
    logger.add("data/raw/metrics.log", rotation="500 MB")
    logger.info("Starting metrics processing for GitHub Peru Analytics")

    users_path = "data/raw/users/peru_users.json"
    repos_path = "data/raw/repos/peru_repos.json"
    classifications_path = "data/processed/classifications.json"

    if not os.path.exists(users_path) or not os.path.exists(repos_path):
        logger.error("Raw data files not found. Run extract_data.py first.")
        return

    with open(users_path, "r", encoding="utf-8") as f:
        users = json.load(f)

    with open(repos_path, "r", encoding="utf-8") as f:
        repos = json.load(f)

    classifications = []
    if os.path.exists(classifications_path):
        with open(classifications_path, "r", encoding="utf-8") as f:
            classifications = json.load(f)
    else:
        logger.warning(f"Classifications file not found at {classifications_path}. Industry metrics will be limited. Run classify_data.py first.")

    # Convert classifications list to dict mapped by repo_id
    classifications_dict = {c.get("repo_id"): c for c in classifications}

    calculator = UserMetricsCalculator()
    processed_users = []

    # Process metrics per user
    for user in users:
        username = user.get("login")
        if not username:
            continue

        # Get repos for this user
        user_repos = [r for r in repos if r.get("owner", {}).get("login") == username]
        
        # Get classifications for these repos
        user_classifications = []
        for r in user_repos:
            repo_id = r.get("id")
            if repo_id in classifications_dict:
                user_classifications.append(classifications_dict[repo_id])
                
        # Calculate metrics using existing calculator
        metrics = calculator.calculate_all_metrics(user, user_repos, user_classifications)
        
        # Combine user info and metrics
        user_data = {
            "username": username,
            "name": user.get("name"),
            "location": user.get("location"),
            "company": user.get("company"),
            "bio": user.get("bio"),
            **metrics
        }
        processed_users.append(user_data)

    df_users = pd.DataFrame(processed_users)

    # Clean lists to be string format for CSV (optional, but good for saving)
    df_users["primary_languages"] = df_users["primary_languages"].apply(lambda x: ", ".join(x) if isinstance(x, list) else x)

    os.makedirs("data/processed", exist_ok=True)
    
    # Save processed users
    csv_path = "data/processed/users_metrics.csv"
    df_users.to_csv(csv_path, index=False)
    logger.info(f"Processed metrics for {len(processed_users)} users saved to {csv_path}")

    # It's also useful to save flattened repos for the dashboard
    repos_flattened = []
    for r in repos:
        repo_id = r.get("id")
        repo_data = {
            "repo_id": repo_id,
            "name": r.get("name"),
            "owner": r.get("owner", {}).get("login"),
            "stars": r.get("stargazers_count", 0),
            "forks": r.get("forks_count", 0),
            "language": r.get("language"),
            "topics": ", ".join(r.get("topics", [])),
            "description": r.get("description"),
            "industry_code": classifications_dict.get(repo_id, {}).get("industry_code"),
            "industry_name": classifications_dict.get(repo_id, {}).get("industry_name"),
            "industry_confidence": classifications_dict.get(repo_id, {}).get("confidence"),
        }
        repos_flattened.append(repo_data)

    df_repos = pd.DataFrame(repos_flattened)
    repos_csv_path = "data/processed/repos_metrics.csv"
    df_repos.to_csv(repos_csv_path, index=False)
    logger.info(f"Processed metrics for {len(repos_flattened)} repos saved to {repos_csv_path}")


if __name__ == "__main__":
    main()
