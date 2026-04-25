from bs4 import BeautifulSoup

def analyze_seo(html_content: str):
    """
    Parses HTML content and evaluates basic SEO metrics.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Initialize results
    results = {
        "title": None,
        "meta_description": None,
        "h1_count": 0,
        "h2_count": 0,
        "h3_count": 0,
        "total_images": 0,
        "images_missing_alt": 0,
        "issues": []
    }

    # 1. Analyze Title
    title_tag = soup.find("title")
    if title_tag:
        results["title"] = title_tag.get_text().strip()
    else:
        results["issues"].append("Missing <title> tag")

    # 2. Analyze Meta Description
    meta_desc = soup.find("meta", attrs={"name": "description"})
    if meta_desc:
        results["meta_description"] = meta_desc.get("content", "").strip()
    else:
        results["issues"].append("Missing <meta name='description'> tag")

    # 3. Analyze Headings
    results["headings"] = {
        "h1": len(soup.find_all("h1")),
        "h2": len(soup.find_all("h2")),
        "h3": len(soup.find_all("h3")),
        "h4": len(soup.find_all("h4")),
        "h5": len(soup.find_all("h5")),
        "h6": len(soup.find_all("h6")),
    }

    if results["headings"]["h1"] == 0:
        results["issues"].append("No <h1> tag found")
    elif results["headings"]["h1"] > 1:
        results["issues"].append(f"Multiple <h1> tags found ({results['headings']['h1']})")
    # 4. Analyze Images
    images = soup.find_all("img")
    results["total_images"] = len(images)
    
    missing_alt = 0
    for img in images:
        if not img.get("alt"):
            missing_alt += 1
            
    results["images_missing_alt"] = missing_alt
    if missing_alt > 0:
        results["issues"].append(f"{missing_alt} image(s) missing 'alt' attribute")

    # 5. Canonical URL
    canonical = soup.find("link", rel="canonical")
    results["canonical"] = canonical.get("href") if canonical else None
    if not results["canonical"]:
        results["issues"].append("Missing <link rel='canonical'> tag")

    # 6. Social Meta (Open Graph)
    og_title = soup.find("meta", property="og:title")
    og_desc = soup.find("meta", property="og:description")
    og_image = soup.find("meta", property="og:image")
    results["social_meta"] = {
        "og:title": og_title.get("content") if og_title else None,
        "og:description": og_desc.get("content") if og_desc else None,
        "og:image": og_image.get("content") if og_image else None
    }
    if not og_title or not og_desc:
        results["issues"].append("Missing Open Graph (og:title/og:description) meta tags")

    # 7. Structured Data (JSON-LD)
    scripts = soup.find_all("script", type="application/ld+json")
    results["structured_data"] = {
        "count": len(scripts),
        "present": len(scripts) > 0
    }
    if not results["structured_data"]["present"]:
        results["issues"].append("No JSON-LD structured data found")

    return results

def calculate_seo_score(seo_data: dict, tech_data: dict):
    """
    Calculates a comprehensive SEO score (0-100) based on multiple categories.
    """
    scores = {
        "on_page": 0,
        "technical": 0,
        "performance": 0,
        "accessibility": 0
    }

    # --- A) On-Page SEO (40 Points) ---
    # 1. Title (10 pts)
    title = seo_data.get("title")
    if title:
        scores["on_page"] += 5
        if 50 <= len(title) <= 60:
            scores["on_page"] += 5
    
    # 2. Meta Description (10 pts)
    meta = seo_data.get("meta_description")
    if meta:
        scores["on_page"] += 5
        if 120 <= len(meta) <= 160:
            scores["on_page"] += 5

    # 3. Headings (10 pts)
    headings = seo_data.get("headings", {})
    if headings.get("h1", 0) >= 1:
        scores["on_page"] += 5
        # Hierarchy: Check if H1 exists and is singular for "proper" hierarchy point
        if headings.get("h1") == 1:
            scores["on_page"] += 5

    # 4. Images On-Page (10 pts)
    total_imgs = seo_data.get("total_images", 0)
    missing_alt = seo_data.get("images_missing_alt", 0)
    if total_imgs > 0:
        coverage = (total_imgs - missing_alt) / total_imgs
        scores["on_page"] += coverage * 10

    # --- B) Technical SEO (30 Points) ---
    if tech_data.get("is_https"):
        scores["technical"] += 10
    if tech_data.get("has_sitemap"):
        scores["technical"] += 10
    if tech_data.get("has_robots"):
        scores["technical"] += 10

    # --- C) Performance (20 Points) ---
    load_time = tech_data.get("load_time", 10)
    if load_time < 3:
        scores["performance"] += 10
    elif load_time < 5:
        scores["performance"] += 5
    
    # Simple logic for Page Size/Resources
    html_size_kb = tech_data.get("html_size_kb", 0)
    if 0 < html_size_kb < 200:
        scores["performance"] += 10
    elif html_size_kb < 500:
        scores["performance"] += 5

    # --- D) Accessibility (10 Points) ---
    if total_imgs > 0:
        coverage = (total_imgs - missing_alt) / total_imgs
        scores["accessibility"] += coverage * 10
    else:
        scores["accessibility"] += 10 # Perfect if no images to fail on

    # Total Score
    total_score = sum(scores.values())

    return {
        "seo_score": round(total_score, 1),
        "category_scores": {k: round(v, 1) for k, v in scores.items()}
    }
