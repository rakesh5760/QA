import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_analyze_basic(target_url):
    print(f"\n--- Testing AI Integration with target: {target_url} ---")
    start_time = time.time()
    try:
        response = requests.post(f"{BASE_URL}/analyze-basic", json={"url": target_url}, timeout=120)
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            bug_report = data.get("bug_report")
            
            ai_insights = data.get("ai_insights")
            
            if bug_report:
                print(f"Request took: {end_time - start_time:.2f} seconds")
                # ... existing prints ...
                
                if ai_insights:
                    print("\n--- AI Insights ---")
                    print(json.dumps(ai_insights, indent=2))
                else:
                    print("\n--- AI Insights: MISSING ---")
                
                # Check for structure correctness
                required_fields = ["total_links_checked", "valid_links", "broken_links", "server_errors"]
                if all(field in bug_report for field in required_fields):
                    print("Structure Check: PASSED")
                else:
                    print("Structure Check: FAILED (missing fields)")
                
                return data
            else:
                print("FAILED: bug_report missing from response")
        else:
            print(f"FAILED: Status Code {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"ERROR: {e}")
    return None

if __name__ == "__main__":
    # 1. Test with a real site (or a mock site that has broken links)
    # Using httpbin.org/links which has relative links and some may be broken depending on configuration
    test_analyze_basic("https://httpbin.org/links/3/0")
    
    # 2. Test with edge cases if possible
    # We'll use a site known for diverse link types if possible, or just observe the previous output
