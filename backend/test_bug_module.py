import json
import sys
import os

# Add backend to path so we can import services
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.bug_service import detect_bugs

test_links = [
    "https://www.google.com",              # Valid
    "https://httpbin.org/status/404",      # Broken
    "https://httpbin.org/status/500",      # Server Error
    "invalid-url",                         # Invalid
    "mailto:test@example.com",              # Filtered
    "https://httpbin.org/delay/10"         # Should timeout (if threshold is 5s)
]

print(f"Testing detect_bugs directly with {len(test_links)} links...")
results = detect_bugs(test_links)

print("Bug Report Results:")
print(json.dumps(results, indent=2))

# Basic validation
if results["total_links_checked"] > 0:
    print("Verification PASSED: detect_bugs returned a structured report.")
    
    # Check if specific status codes were caught
    broken_urls = [b["url"] for b in results["broken_links"]]
    if any("404" in url or "Timeout" in str(b.get("status_code")) for b, url in zip(results["broken_links"], broken_urls)):
         print("Validation: Successfully detected broken links/timeouts.")
else:
    print("Verification FAILED: No links were checked or error occurred.")
