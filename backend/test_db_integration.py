import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def verify_step_9():
    print("--- 1. Testing analysis and insertion ---")
    target_url = "https://httpbin.org/get"
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/analyze-basic", json={"url": target_url}, timeout=120)
    
    if response.status_code == 200:
        data = response.json()
        record_id = data.get("id")
        created_at = data.get("created_at")
        print(f"Success! Analysis completed in {time.time() - start_time:.2f}s")
        print(f"Record ID: {record_id}, Created At: {created_at}")
        
        if not record_id or not created_at:
            print("FAILED: Missing id or created_at in response")
            return

        print("\n--- 2. Verifying history list ---")
        hist_response = requests.get(f"{BASE_URL}/history")
        if hist_response.status_code == 200:
            history = hist_response.json()
            print(f"History count: {len(history)}")
            
            # Check for required fields in history items
            if len(history) > 0:
                item = history[0]
                if all(k in item for k in ["id", "url", "created_at", "result"]):
                    print("PASSED: History structure is correct.")
                else:
                    print(f"FAILED: History item structure missing keys. Keys found: {list(item.keys())}")
            else:
                print("FAILED: History is empty after insertion.")
        else:
            print(f"FAILED: /history returned {hist_response.status_code}")

        print(f"\n--- 3. Verifying detail retrieval for ID {record_id} ---")
        detail_response = requests.get(f"{BASE_URL}/history/{record_id}")
        if detail_response.status_code == 200:
            detail = detail_response.json()
            if detail["id"] == record_id and detail["url"] == target_url:
                print("PASSED: Returned record correctly matches the requested ID and URL.")
                # Verify JSON structure
                if "result" in detail and isinstance(detail["result"], dict):
                    print("PASSED: result column correctly deserialized to dict.")
                else:
                    print("FAILED: result is missing or not a dictionary.")
            else:
                print(f"FAILED: Data mismatch in detail view.")
        else:
            print(f"FAILED: /history/{record_id} returned {detail_response.status_code}")

        print("\n--- 4. Testing Edge Case: Invalid ID ---")
        invalid_id = 999999
        invalid_response = requests.get(f"{BASE_URL}/history/{invalid_id}")
        if invalid_response.status_code == 404:
            print(f"PASSED: Correctly handled invalid ID {invalid_id} with 404.")
        else:
            print(f"FAILED: Expected 404 for invalid ID, got {invalid_response.status_code}")

    else:
        print(f"FAILED: /analyze-basic failed with status {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    verify_step_9()
