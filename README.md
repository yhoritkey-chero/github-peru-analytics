# GitHub Peru Analytics

## 1. Project Title and Description
GitHub Peru Analytics is a data analytics platform that extracts, processes, and visualizes information about the Peruvian developer ecosystem using the GitHub API.

## 2. Key Findings
(To be filled after analysis)

## 3. Data Collection
Data is collected via the GitHub API using `requests` and `tenacity` for rate limiting.

## 4. Features
- Data Extraction (Users & Repos)
- GPT-4 Classification
- Metrics Calculation
- Streamlit Dashboard

## 5. Installation
```bash
pip install -r requirements.txt
cp .env.example .env
# Add your GitHub & OpenAI tokens
```

## 6. Usage
```bash
python scripts/extract_data.py
streamlit run app/main.py
```

## 7. Metrics Documentation
- Total Repos
- Stars Received
- etc...

## 8. AI Agent Documentation
We use OpenAI GPT-4 for batch classification of GitHub repositories into 21 CIIU industry categories.

## 9. Limitations
- GitHub API Limits (5000 requests/hour)
- Only users specifying 'Peru' in location are tracked

## 10. Author Information
chero
