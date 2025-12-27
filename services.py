import os
import json
from openai import OpenAI

class LLMService:
    def __init__(self, api_key=None):
       
        self.client = OpenAI(api_key=api_key) if api_key else None

    def generate_completion(self, prompt: str, system_role: str = "You are a helpful AI assistant.") -> str:
        if not self.client:
            return "MOCK RESPONSE: LLM API Key not found."
            
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",  
                messages=[
                    {"role": "system", "content": system_role},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error generating content: {str(e)}"

    def generate_json(self, prompt: str, system_role: str) -> dict:
        """Helper to ensure JSON output from LLM"""
        content = self.generate_completion(prompt + "\n\nOutput strictly valid JSON only.", system_role)
        
        content = content.replace("```json", "").replace("```", "").strip()
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {"error": "Failed to parse JSON", "raw": content}