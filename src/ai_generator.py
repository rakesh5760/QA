import os
import json
import logging
import requests

logger = logging.getLogger(__name__)

class AIGenerator:
    def __init__(self, model="llama-3.3-70b-versatile", temperature=0.3):
        self.model = model
        self.temperature = temperature
        self.api_key = os.getenv("GROQ_API_KEY")
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        
    def generate_form_test_data(self, form_schema):
        """
        Uses Groq AI to generate 2 valid and 2 invalid sets of test data based on form schema.
        """
        if not self.api_key:
            logger.warning("GROQ_API_KEY is not set. Skipping AI data generation.")
            return {"valid": [], "invalid": []}
            
        system_prompt = (
            "You are a QA test data generator. "
            "Given the following form fields (array of objects with 'name', 'type', 'label', 'required'), "
            "generate two valid test data objects and two invalid test data objects. "
            "Return ONLY a JSON object with keys: 'valid': [ {...}, {...} ], 'invalid': [ {...}, {...} ]. "
            "Do not return any markdown wrapping like ```json, just the raw JSON object."
        )
        
        user_prompt = f"Form fields: {json.dumps(form_schema)}"
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": self.temperature,
            "response_format": {"type": "json_object"}
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            ai_content = response.json()['choices'][0]['message']['content']
            test_data = json.loads(ai_content)
            
            # Basic validation of returned structure
            if "valid" not in test_data or "invalid" not in test_data:
                logger.error("AI returned malformed JSON structure.")
                return {"valid": [], "invalid": []}
                
            return test_data
        except Exception as e:
            logger.error(f"Failed to generate form test data via Groq: {e}")
            return {"valid": [], "invalid": []}
