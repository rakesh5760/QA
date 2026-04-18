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
    results["h1_count"] = len(soup.find_all("h1"))
    results["h2_count"] = len(soup.find_all("h2"))
    results["h3_count"] = len(soup.find_all("h3"))

    if results["h1_count"] == 0:
        results["issues"].append("No <h1> tag found")
    elif results["h1_count"] > 1:
        results["issues"].append(f"Multiple <h1> tags found ({results['h1_count']})")

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

    return results
