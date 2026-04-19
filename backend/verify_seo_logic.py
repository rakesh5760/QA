from backend.services.seo_service import calculate_seo_score

def test_logic():
    print("--- Testing SEO Scoring Logic (Mock Data) ---")
    
    # Base tech data (perfect tech score)
    tech = {
        "is_https": True,
        "has_sitemap": True,
        "has_robots": True,
        "load_time": 1,
        "html_size_kb": 10
    }
    
    # 1. Baseline (Perfect On-Page)
    seo_perfect = {
        "title": "A Perfect Title for Testing SEO Scoring Utility 55-60", # 55 chars
        "meta_description": "This is a perfect meta description for testing the SEO scoring engine of our QA automation system. 120-160 characters long and very detailed.", # 140 chars
        "headings": {"h1": 1},
        "total_images": 1,
        "images_missing_alt": 0
    }
    
    score_p = calculate_seo_score(seo_perfect, tech)
    print(f"Perfect Score: {score_p['seo_score']} (Expected near 100)")
    
    # 2. Remove Title
    seo_no_title = seo_perfect.copy()
    seo_no_title["title"] = None
    score_no_title = calculate_seo_score(seo_no_title, tech)
    diff = score_p['seo_score'] - score_no_title['seo_score']
    print(f"No Title Score: {score_no_title['seo_score']} (Decrease: {diff}) - Expected -10")
    
    # 3. Remove Meta Description
    seo_no_meta = seo_perfect.copy()
    seo_no_meta["meta_description"] = None
    score_no_meta = calculate_seo_score(seo_no_meta, tech)
    diff = score_p['seo_score'] - score_no_meta['seo_score']
    print(f"No Meta Score: {score_no_meta['seo_score']} (Decrease: {diff}) - Expected -10")

    # 4. Image Alt logic
    seo_images = seo_perfect.copy()
    seo_images["total_images"] = 10
    seo_images["images_missing_alt"] = 10
    score_bad_alt = calculate_seo_score(seo_images, tech)
    
    seo_good_alt = seo_images.copy()
    seo_good_alt["images_missing_alt"] = 0
    score_good_alt = calculate_seo_score(seo_good_alt, tech)
    
    diff = score_good_alt['seo_score'] - score_bad_alt['seo_score']
    print(f"Add Alt Text (0/10 -> 10/10) Score Increase: {diff:.1f} - Expected +20 (10 in On-Page, 10 in Accessibility)")

if __name__ == "__main__":
    test_logic()
