import asyncio
import logging
from src.extractor import extract_forms
from src.ai_generator import AIGenerator
from src.utils import create_screenshot_path

logger = logging.getLogger(__name__)

class TestRunner:
    def __init__(self, ai_generator: AIGenerator, output_dir: str):
        self.ai = ai_generator
        self.output_dir = output_dir

    async def run_form_tests(self, page, url):
        """
        Extracts forms, generates test data, and runs Playwright tests for valid/invalid inputs.
        """
        forms = await extract_forms(page)
        results = []
        
        for form in forms:
            logger.info(f"Testing form {form['id']} on {url}")
            test_data = self.ai.generate_form_test_data(form["fields"])
            
            form_result = {
                "form_id": form["id"],
                "valid_tests": [],
                "invalid_tests": []
            }
            
            # Test Valid Data
            for idx, data_set in enumerate(test_data.get("valid", [])):
                res = await self._execute_form_submission(page, url, form, data_set, is_valid=True, test_idx=idx)
                form_result["valid_tests"].append(res)
                
            # Test Invalid Data
            for idx, data_set in enumerate(test_data.get("invalid", [])):
                res = await self._execute_form_submission(page, url, form, data_set, is_valid=False, test_idx=idx)
                form_result["invalid_tests"].append(res)
                
            results.append(form_result)
            
        return results

    async def _execute_form_submission(self, page, url, form, data_set, is_valid, test_idx):
        """
        Fills the form with data_set and submits it. Checks for success or failure.
        """
        # Reload the page to ensure a clean state
        await page.goto(url, wait_until="domcontentloaded")
        
        result = {
            "data_used": data_set,
            "passed": False,
            "screenshot": None,
            "error_msg": None
        }
        
        try:
            # Fill out fields
            for field in form["fields"]:
                name = field["name"]
                if name in data_set:
                    value = str(data_set[name])
                    field_type = field["type"]
                    selector = f"form#{form['id']} [name='{name}']"
                    
                    # Try to fill based on type
                    element = await page.query_selector(selector)
                    if element:
                        if field_type in ["checkbox", "radio"]:
                            if str(value).lower() in ["true", "1", "yes"]:
                                await element.check()
                            else:
                                await element.uncheck()
                        elif field_type == "select":
                            await page.select_option(selector, value)
                        else:
                            await element.fill(value)
            
            # Submit form
            submit_btn = await page.query_selector(f"form#{form['id']} [type='submit'], form#{form['id']} button")
            if submit_btn:
                await submit_btn.click()
            else:
                await page.evaluate(f"document.getElementById('{form['id']}').submit()")
                
            await asyncio.sleep(2) # Wait for potential inline messages
            
            # Verify based on expectation
            if is_valid:
                # We expect NO 500 errors, maybe a success message, or navigation
                # For a simple check: see if there are any visible elements containing "error" or "invalid"
                error_el = await page.query_selector("*:has-text('error'), *:has-text('invalid')")
                if error_el:
                    result["passed"] = False
                    result["error_msg"] = "Found error text on valid submission."
                else:
                    result["passed"] = True
            else:
                # We expect an inline error message or validation failure
                error_el = await page.query_selector("*:has-text('error'), *:has-text('invalid'), *:has-text('required')")
                validation_msg = await page.evaluate(f"""() => {{
                    const form = document.getElementById('{form['id']}');
                    if (!form) return false;
                    return !form.checkValidity();
                }}""")
                
                if error_el or validation_msg:
                    result["passed"] = True
                else:
                    result["passed"] = False
                    result["error_msg"] = "Form accepted invalid data without showing errors."
                    
        except Exception as e:
            logger.error(f"Error executing form test: {e}")
            result["error_msg"] = str(e)
            result["passed"] = False
            
        if not result["passed"]:
            shot_path = create_screenshot_path(os.path.join(self.output_dir, "screenshots"))
            await page.screenshot(path=shot_path, full_page=True)
            result["screenshot"] = shot_path
            
        return result
