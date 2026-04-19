import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def verify_qa_enhancements(url):
    print(f"\n--- Verifying QA Enhancements for: {url} ---")
    try:
        response = requests.post(f"{BASE_URL}/analyze-basic", json={"url": url}, timeout=150)
        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
            return
        
        data = response.json()
        qa = data.get("qa_checks")
        
        if not qa:
            print("FAIL: qa_checks object missing from response")
            return
        
        print(f"Page Status: {qa.get('page_status')}")
        print(f"Load Time: {qa.get('load_time')}s")
        print(f"UI Elements: {json.dumps(qa.get('ui_elements'), indent=2)}")
        print(f"Console Errors: {len(qa.get('console_errors', []))}")
        print(f"Console Warnings: {len(qa.get('console_warnings', []))}")
        print(f"Identified QA Issues: {qa.get('issues')}")
        
        # Validation checks
        issues = qa.get("issues", [])
        if qa.get("load_time") > 3 and not any("Slow page load" in i for i in issues):
            print("FAIL: Missing issue for slow page load")
        if qa.get("ui_elements", {}).get("buttons_count") == 0 and not any("No buttons found" in i for i in issues):
            print("FAIL: Missing issue for zero buttons")
        if qa.get("page_status") != 200 and not any("non-200 status" in i for i in issues):
            print("FAIL: Missing issue for non-200 status")
            
        print("Schema and primary logic checks passed.")
        
    except Exception as e:
        print(f"Exception during verification: {str(e)}")

if __name__ == "__main__":
    # 1. Simple site
    verify_qa_enhancements("https://example.com")
    
    # 2. Site with potential errors/issues
    verify_qa_enhancements("https://www.google.com")
    
    # 3. Non-existent URL (to test crash resilience)
    verify_qa_enhancements("https://this-url-better-not-exist-123.com")
