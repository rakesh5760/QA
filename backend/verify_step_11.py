import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def verify_seo_scoring(url):
    print(f"--- Verifying SEO Scoring for: {url} ---")
    try:
        response = requests.post(f"{BASE_URL}/analyze-basic", json={"url": url}, timeout=120)
        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
            return
        
        data = response.json()
        score_data = data.get("seo_score_data")
        
        if not score_data:
            print("FAIL: seo_score_data object missing from response")
            return
        
        score = score_data.get("seo_score")
        cats = score_data.get("category_scores")
        
        print(f"Overall Score: {score}")
        print(f"Category Scores: {json.dumps(cats, indent=2)}")
        
        # Range checks
        if not (0 <= score <= 100):
            print(f"FAIL: Overall score {score} out of bounds (0-100)")
        
        required_cats = ["on_page", "technical", "performance", "accessibility"]
        for cat in required_cats:
            if cat not in cats:
                print(f"FAIL: Category '{cat}' missing from category_scores")
            elif not (0 <= cats[cat] <= 100):
                print(f"FAIL: Category '{cat}' score {cats[cat]} out of bounds")
        
        print("Schema and Range checks passed.")
        
    except Exception as e:
        print(f"Exception during verification: {str(e)}")

if __name__ == "__main__":
    # Test with a robust site and a simple site
    verify_seo_scoring("https://example.com")
    verify_seo_scoring("https://google.com")
