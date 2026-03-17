import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv
import json

class InsightsAgent:
    def __init__(self, users_csv_path: str, repos_csv_path: str):
        """Initialize the agent with paths to our processed CSV data."""
        import os
        try:
            import streamlit as st
            if "OPENAI_API_KEY" in st.secrets:
                self.client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
            else:
                load_dotenv()
                self.client = OpenAI()
        except Exception:
            load_dotenv()
            self.client = OpenAI()
            
        self.users_df = pd.read_csv(users_csv_path)
        self.repos_df = pd.read_csv(repos_csv_path)
        
        # Prepare context summaries to inject into the prompt
        self.ecosystem_summary = self._generate_ecosystem_summary()

    def _generate_ecosystem_summary(self) -> str:
        """Create a compact statistical summary of the dataset for the LLM."""
        total_devs = len(self.users_df)
        total_repos = len(self.repos_df)
        total_stars = int(self.users_df['total_stars_received'].sum())
        
        # Top languages safely
        top_langs = self.repos_df['language'].value_counts().head(5).to_dict() if 'language' in self.repos_df.columns else {}
        
        # Top industries safely
        top_industries = self.repos_df['industry_name'].value_counts().head(5).to_dict() if 'industry_name' in self.repos_df.columns else {}
        
        # Top 5 developers by Impact Score
        top_devs = self.users_df.nlargest(5, 'impact_score')[['username', 'impact_score', 'total_stars_received']].to_dict('records')
        
        summary = f"""
        DATASET SUMMARY (PERU DEVELOPER ECOSYSTEM):
        - Total Developers Tracked: {total_devs}
        - Total Repositories Tracked: {total_repos}
        - Total Stars Received: {total_stars}
        
        Top 5 Programming Languages:
        {json.dumps(top_langs, indent=2)}
        
        Top 5 Industries Served (CIIU):
        {json.dumps(top_industries, indent=2)}
        
        Top 5 Developers (by Impact Score):
        {json.dumps(top_devs, indent=2)}
        """
        return summary

    def ask(self, user_question: str) -> str:
        """Answer queries based on the pre-computed ecosystem statistics."""
        
        system_prompt = f"""
        Eres el 'Agente de Insights de Antigravity', un experto analista de datos para el proyecto GitHub Peru Analytics.
        Tu trabajo es responder preguntas sobre el ecosistema de desarrolladores peruanos usando ÚNICAMENTE el contexto estadístico proporcionado a continuación.
        
        CONTEXTO:
        {self.ecosystem_summary}
        
        REGLAS:
        1. Responde SIEMPRE en ESPAÑOL de forma concisa y profesional.
        2. Si el usuario pregunta por datos no presentes en el CONTEXTO, indica amablemente que solo tienes acceso a las métricas de resumen proporcionadas.
        3. No inventes ni alucines desarrolladores, repositorios o estadísticas.
        4. Si te preguntan por tus creadores o identidad, menciona que eres parte del proyecto 'GitHub Peru Analytics' desarrollado por chero y Antigravity.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_question}
                ],
                temperature=0.4,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error connecting to AI Agent: {str(e)}"
