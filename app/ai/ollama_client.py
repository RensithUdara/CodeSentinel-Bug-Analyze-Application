"""
AI suggestions via Ollama.
"""
import requests
import json
from typing import Optional


class OllamaClient:
    def __init__(self, model='codellama:7b', base_url='http://localhost:11434'):
        self.base_url = base_url
        self.model = model

    def is_available(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except Exception:
            return False

    def suggest_refactoring(self, code_snippet: str, issue_description: str) -> str:
        if not self.is_available():
            return "Ollama service not available. Please start it with `ollama serve`."
        prompt = f"""You are an expert software engineer. The following code has a problem:
{issue_description}

Code:
{code_snippet}

Suggest a specific refactoring. Provide only the refactored code and a short explanation (1-2 sentences) after the code."""
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=60
            )
            if response.status_code == 200:
                return response.json().get('response', '')
            return f"Error: {response.status_code}"
        except Exception as e:
            return f"Error contacting Ollama: {e}"
