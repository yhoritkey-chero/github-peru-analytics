from openai import OpenAI
import json

class IndustryClassifier:
    def __init__(self):
        self.client = OpenAI()
        self.industries = {
            "A": "Agriculture, forestry and fishing",
            "B": "Mining and quarrying",
            "C": "Manufacturing",
            "D": "Electricity, gas, steam supply",
            "E": "Water supply; sewerage",
            "F": "Construction",
            "G": "Wholesale and retail trade",
            "H": "Transportation and storage",
            "I": "Accommodation and food services",
            "J": "Information and communication",
            "K": "Financial and insurance activities",
            "L": "Real estate activities",
            "M": "Professional, scientific activities",
            "N": "Administrative and support activities",
            "O": "Public administration and defense",
            "P": "Education",
            "Q": "Human health and social work",
            "R": "Arts, entertainment and recreation",
            "S": "Other service activities",
            "T": "Activities of households",
            "U": "Extraterritorial organizations"
        }

    def classify_repository(self, name: str, description: str, readme: str, topics: list[str], language: str) -> dict:
        prompt = f"""Analyze this GitHub repository and classify it into ONE of the following industry categories based on its potential application or the industry it serves.

REPOSITORY INFORMATION:
- Name: {name}
- Description: {description or 'No description'}
- Primary Language: {language or 'Not specified'}
- Topics: {', '.join(topics) if topics else 'None'}
- README (first 2000 chars): {readme[:2000] if readme else 'No README'}

INDUSTRY CATEGORIES:
{json.dumps(self.industries, indent=2)}

INSTRUCTIONS:
1. Analyze the repository's purpose, functionality, and potential use cases
2. Consider what industry would most benefit from or use this software
3. If it's a general-purpose tool (e.g., utility library), classify based on the most likely industry application
4. If truly generic (e.g., "hello world"), use "J" (Information and communication)

Respond in JSON format:
{{
    "industry_code": "X",
    "industry_name": "Full industry name",
    "confidence": "high|medium|low",
    "reasoning": "Brief explanation of why this classification was chosen"
}}
"""
        response = self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are an expert at classifying software projects by industry. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)

    def batch_classify(self, repositories: list[dict], batch_size: int = 10) -> list[dict]:
        results = []
        for i in range(0, len(repositories), batch_size):
            batch = repositories[i:i+batch_size]
            for repo in batch:
                classification = self.classify_repository(
                    name=repo.get("name", ""),
                    description=repo.get("description", ""),
                    readme=repo.get("readme", ""),
                    topics=repo.get("topics", []),
                    language=repo.get("language", "")
                )
                results.append({
                    "repo_id": repo["id"],
                    "repo_name": repo["name"],
                    **classification
                })
        return results
