import os
import json
from loguru import logger
from dotenv import load_dotenv
from src.classification.industry_classifier import IndustryClassifier

def main():
    load_dotenv()
    logger.add("data/raw/classification.log", rotation="500 MB")
    logger.info("Starting data classification for GitHub Peru Analytics")

    repos_path = "data/raw/repos/peru_repos.json"
    if not os.path.exists(repos_path):
        logger.error(f"Repos file not found at {repos_path}. Please run extract_data.py first.")
        return

    with open(repos_path, "r", encoding="utf-8") as f:
        repos = json.load(f)

    logger.info(f"Loaded {len(repos)} repositories.")

    # NOTE: You can uncomment the line below to test with a smaller batch (e.g., 50) 
    # and not consume too many OpenAI tokens at first.
    # repos = repos[:50] 

    classifier = IndustryClassifier()
    
    logger.info("Starting batch classification... This might take some time and consume OpenAI tokens.")
    classifications = classifier.batch_classify(repos, batch_size=10)

    os.makedirs("data/processed", exist_ok=True)
    classifications_path = "data/processed/classifications.json"
    
    with open(classifications_path, "w", encoding="utf-8") as f:
        json.dump(classifications, f, indent=2)

    logger.info(f"Classification successfully saved at {classifications_path}")

if __name__ == "__main__":
    main()
