import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_ai_insights(seo_analysis, bug_report):
    """
    Consolidated AI insights from Groq API.
    """
    key = os.getenv("GROQ_API_KEY")
    GROQ_API_KEY = key.strip() if key else None
    GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

    if not GROQ_API_KEY:
        print("AI Service: Missing GROQ_API_KEY")
        return get_fallback_insights()

    system_prompt = (
        "You are an AI-powered QA Automation Expert. "
        "Analyze the provided website data and respond ONLY with a valid JSON object. "
        "Include the string 'json' in your response structure."
    )
    
    user_prompt = f"""
    Provide:
    1. 5 functional test cases.
    2. A 2-sentence bug summary.
    3. 3 fix suggestions.

    SEO Data: {json.dumps(seo_analysis)}
    Bug Report: {json.dumps(bug_report)}

    Expected JSON Format:
    {{
        "test_cases": [],
        "bug_summary": "",
        "fix_suggestions": []
    }}
    """

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.2
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=20)
        if response.status_code != 200:
            print(f"Groq API Error {response.status_code}: {response.text}")
            return get_fallback_insights()
            
        ai_response = response.json()
        content = ai_response['choices'][0]['message']['content']
        
        # Simple extraction in case it's wrapped in markdown
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        return json.loads(content)

    except Exception as e:
        print(f"AI Service Exception: {e}")
        return get_fallback_insights()

def get_fallback_insights():
    return {
        "test_cases": ["Verify page loads", "Check meta tags"],
        "bug_summary": "AI analysis failed, but technical errors were found in the report.",
        "fix_suggestions": ["Optimize SEO tags", "Fix broken links"]
    }

# Wrappers for specific requirements
def generate_test_cases(data):
    return get_ai_insights(data.get('seo_analysis', {}), data.get('bug_report', {})).get("test_cases", [])

def summarize_bugs(bug_report):
    return get_ai_insights({}, bug_report).get("bug_summary", "")

def suggest_fixes(seo_analysis, bug_report):
    return get_ai_insights(seo_analysis, bug_report).get("fix_suggestions", [])
