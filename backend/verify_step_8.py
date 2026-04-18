import requests
import json
import time
import os

BASE_URL = "http://127.0.0.1:8000"

def test_ai_integration(target_url, api_key_valid=True):
    print(f"\n--- Testing AI Integration (Valid Key: {api_key_valid}) ---")
    print(f"Target URL: {target_url}")
    
    start_time = time.time()
    try:
        # If we want to simulate an invalid key, we can't easily change the .env 
        # but we can pass a header or something if our service allowed it.
        # For this test, we'll assume the .env is correct for the first call.
        
        response = requests.post(f"{BASE_URL}/analyze-basic", json={"url": target_url}, timeout=120)
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            ai_insights = data.get("ai_insights")
            
            if ai_insights:
                print(f"Request Duration: {end_time - start_time:.2f}s")
                print("\nAI Insights Structure:")
                print(f"- test_cases: {type(ai_insights.get('test_cases'))} (count: {len(ai_insights.get('test_cases', []))})")
                print(f"- bug_summary: {type(ai_insights.get('bug_summary'))}")
                print(f"- fix_suggestions: {type(ai_insights.get('fix_suggestions'))} (count: {len(ai_insights.get('fix_suggestions', []))})")
                
                print("\nContent Highlights:")
                print(f"Bug Summary: {ai_insights.get('bug_summary')}")
                print(f"Sample Fix: {ai_insights.get('fix_suggestions')[0] if ai_insights.get('fix_suggestions') else 'N/A'}")
                
                # Check for structure correctness
                if all(k in ai_insights for k in ["test_cases", "bug_summary", "fix_suggestions"]):
                    print("\nVerification Status: PASSED (Structure & Content)")
                else:
                    print("\nVerification Status: FAILED (Missing keys)")
            else:
                print("Verification Status: FAILED (ai_insights missing)")
        else:
            print(f"FAILED: Status {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    # Test with a site that usually has some SEO issues
    test_ai_integration("https://httpbin.org/links/2/1")
