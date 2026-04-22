import asyncio
import os
import sys
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.playwright_service import analyze_website

async def test_ai_quality_checks():
    # Path to our local test file
    test_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_page.html"))
    test_url = f"file:///{test_file_path}"
    
    print(f"Starting analysis for: {test_url}")
    
    try:
        results = await analyze_website(test_url)
        
        print("\n--- AI Audit Results ---")
        ai = results.get("ai_insights", {})
        
        print(f"Placeholder Issues: {ai.get('placeholder_issues')}")
        print(f"Content Quality: {ai.get('content_quality')}")
        print(f"Bug Summary: {ai.get('bug_summary')}")
        
        # Validation
        has_placeholders = any("Lorem Ipsum" in str(p) or "TBD" in str(p) for p in ai.get('placeholder_issues', []))
        if has_placeholders:
            print("\nVerification SUCCESS: AI detected placeholders correctly.")
        else:
            print("\nVerification WARNING: AI did not explicitly list 'Lorem Ipsum' or 'TBD'. Check JSON above.")
            
        if ai.get('content_quality'):
             print("Verification SUCCESS: AI provided a content quality assessment.")
        else:
            print("Verification FAILED: AI did not provide content quality field.")

    except Exception as e:
        print(f"Analysis Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_ai_quality_checks())
