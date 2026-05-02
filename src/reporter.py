import os
import json
import logging
from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)

class Reporter:
    def __init__(self, output_dir="reports"):
        self.output_dir = output_dir
        self.template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
        
    def generate_report(self, results):
        """
        Saves raw JSON and generates the HTML report.
        """
        logger.info(f"Generating reports in {self.output_dir}")
        
        # Save JSON
        json_path = os.path.join(self.output_dir, "report.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
            
        # Prepare HTML template data
        pass_items = []
        fail_items = []
        human_review = [
            "Subjective UX (intuitiveness, delight)",
            "Touch gestures on real mobile devices",
            "Screen reader full flow (NVDA/VoiceOver)",
            "Visual alignment against Figma mockups",
            "Business logic requiring domain knowledge"
        ]
        
        # Process results to categorize Pass/Fail
        for url_data in results.get("pages", []):
            url = url_data.get("url")
            
            # Scanners
            scanners = url_data.get("scanners", {})
            for scanner_name, scanner_result in scanners.items():
                item = {
                    "url": url,
                    "type": scanner_name.upper(),
                    "details": scanner_result
                }
                if scanner_result.get("passed"):
                    pass_items.append(item)
                else:
                    fail_items.append(item)
                    
            # Forms
            forms = url_data.get("form_tests", [])
            for form in forms:
                for valid_test in form.get("valid_tests", []):
                    item = {
                        "url": url,
                        "type": "FORM_VALID",
                        "form_id": form["form_id"],
                        "details": valid_test
                    }
                    if valid_test.get("passed"):
                        pass_items.append(item)
                    else:
                        fail_items.append(item)
                        
                for invalid_test in form.get("invalid_tests", []):
                    item = {
                        "url": url,
                        "type": "FORM_INVALID",
                        "form_id": form["form_id"],
                        "details": invalid_test
                    }
                    if invalid_test.get("passed"):
                        pass_items.append(item)
                    else:
                        fail_items.append(item)
                        
        template_data = {
            "base_url": results.get("base_url", "Unknown URL"),
            "description": results.get("description", ""),
            "summary": {
                "total_pages": len(results.get("pages", [])),
                "total_passed": len(pass_items),
                "total_failed": len(fail_items)
            },
            "pass_items": pass_items,
            "fail_items": fail_items,
            "human_review": human_review
        }
        
        # Generate HTML
        try:
            env = Environment(loader=FileSystemLoader(self.template_dir))
            template = env.get_template("report_template.html")
            html_content = template.render(data=template_data)
            
            html_path = os.path.join(self.output_dir, "report.html")
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_content)
                
            logger.info(f"Report successfully generated at {html_path}")
        except Exception as e:
            logger.error(f"Failed to generate HTML report: {e}")
