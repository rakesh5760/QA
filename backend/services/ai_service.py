import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_ai_insights(seo_analysis, bug_report, page_text=""):
    """
    Consolidated AI insights from Groq API.
    Now includes placeholder detection and content quality analysis.
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
        "Identity technical bugs, SEO gaps, and content quality issues. "
        "Additionally, for any forms detected, generate a set of valid and invalid test data for every field."
    )
    
    user_prompt = f"""
    Perform a deep QA audit on the Following Data:
    
    1. SEO Data: {json.dumps(seo_analysis)}
    2. Bug Report (Broken Links): {json.dumps(bug_report)}
    3. Visible Page Text: {page_text[:5000]}
    
    Provide your analysis in the following JSON format:
    {{
        "test_cases": ["5 specific functional test cases"],
        "bug_summary": "Technical summary of issues.",
        "fix_suggestions": ["3 actionable suggestions"],
        "placeholder_issues": ["Lorem Ipsum, TBD, etc."],
        "content_quality": "Detailed note on grammar, tone, and readability.",
        "form_test_data": {{
            "valid": [{{"field_name": "example", "value": "test@example.com"}}],
            "invalid": [{{"field_name": "example", "value": "not-an-email", "reason": "Wrong format"}}]
        }}
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
        response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=25)
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
        "fix_suggestions": ["Optimize SEO tags", "Fix broken links"],
        "placeholder_issues": ["Could not analyze text for placeholders"],
        "content_quality": "Unknown (Analysis failed)"
    }

# Wrappers for specific requirements
def generate_test_cases(data):
    return get_ai_insights(data.get('seo_analysis', {}), data.get('bug_report', {}), data.get('page_text', "")).get("test_cases", [])

def summarize_bugs(bug_report):
    return get_ai_insights({}, bug_report).get("bug_summary", "")

def suggest_fixes(seo_analysis, bug_report):
    return get_ai_insights(seo_analysis, bug_report).get("fix_suggestions", [])
