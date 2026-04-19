from backend.services.bug_service import detect_bugs, is_valid_url

def test_validation():
    print("--- Testing URL Validation ---")
    test_cases = [
        ("https://example.com", True),
        ("https://example.com/#section", True),
        ("#section", False),
        ("mailto:test@example.com", False),
        ("tel:+123456789", False),
        ("javascript:void(0)", False),
        ("/", False), # Should be resolved to absolute before coming to bug_service
    ]
    
    for url, expected in test_cases:
        actual = is_valid_url(url)
        print(f"URL: {url:30} | Expected: {expected} | Actual: {actual}")

def test_detection():
    print("\n--- Testing Bug Detection Logic ---")
    links = [
        "https://www.google.com",
        "https://www.google.com/#fragment", # Duplicate of google.com
        "https://www.google.com",           # Duplicate
        "https://www.linkedin.com/in/reidhoffman", # Likely 999/403
        "https://httpstat.us/404",
        "https://httpstat.us/500",
        "mailto:someone@example.com",
        "#internal-anchor"
    ]
    
    report = detect_bugs(links)
    print(f"\nReport Summary (Check count: {report['total_links_checked']})")
    for link in links:
        if is_valid_url(link):
             print(f"Valid Input Link: {link}")
    # Wait: Google (1), LinkedIn (1), 404 (1), 500 (1). Total should be 4.
    
    print(f"Total Checked: {report['total_links_checked']}")
    print(f"Valid Links: {report['valid_links']}")
    print(f"Broken Links: {len(report['broken_links'])}")
    print(f"Server Errors: {len(report['server_errors'])}")
    
    for link in report['broken_links']:
        print(f"BROKEN: {link}")
    for link in report['server_errors']:
        print(f"SERVER ERROR: {link}")

if __name__ == "__main__":
    test_validation()
    test_detection()
