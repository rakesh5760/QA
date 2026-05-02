async def extract_forms(page):
    """
    Extracts all forms and their input fields from a Playwright page.
    Returns a list of dictionaries describing each form.
    """
    forms = []
    form_elements = await page.query_selector_all("form")
    
    for idx, form_el in enumerate(form_elements):
        form_data = {
            "index": idx,
            "id": await form_el.get_attribute("id") or f"form_{idx}",
            "action": await form_el.get_attribute("action") or "",
            "method": await form_el.get_attribute("method") or "get",
            "fields": []
        }
        
        # Get all inputs inside this form
        inputs = await form_el.query_selector_all("input, select, textarea")
        for input_el in inputs:
            tag_name = await input_el.evaluate("el => el.tagName.toLowerCase()")
            field_type = await input_el.get_attribute("type") or ("text" if tag_name == "input" else tag_name)
            
            # Skip submit buttons, hidden fields
            if field_type in ["submit", "button", "hidden"]:
                continue
                
            name = await input_el.get_attribute("name") or await input_el.get_attribute("id") or "unnamed"
            required = await input_el.get_attribute("required") is not None
            
            # Try to find a label
            label_text = ""
            id_attr = await input_el.get_attribute("id")
            if id_attr:
                label_el = await page.query_selector(f"label[for='{id_attr}']")
                if label_el:
                    label_text = await label_el.inner_text()
            
            if not label_text:
                label_text = await input_el.get_attribute("placeholder") or name
                
            form_data["fields"].append({
                "name": name,
                "type": field_type,
                "label": label_text.strip(),
                "required": required
            })
            
        if form_data["fields"]:
            forms.append(form_data)
            
    return forms

async def extract_links(page):
    """Extracts all links from a page."""
    links = []
    a_tags = await page.query_selector_all("a[href]")
    for a in a_tags:
        href = await a.get_attribute("href")
        if href and not href.startswith(("javascript:", "mailto:", "tel:")):
            links.append(href)
    return links

async def extract_images(page):
    """Extracts images and their alt tags."""
    images = []
    img_tags = await page.query_selector_all("img")
    for img in img_tags:
        src = await img.get_attribute("src")
        alt = await img.get_attribute("alt")
        if src:
            images.append({"src": src, "alt": alt})
    return images
