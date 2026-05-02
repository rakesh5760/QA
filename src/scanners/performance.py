import json
import logging
import subprocess
import tempfile
import os

logger = logging.getLogger(__name__)

def run_performance_audit(url, threshold=0.7):
    """
    Runs Lighthouse CLI via subprocess for performance metrics.
    If Lighthouse is not installed, returns a fallback error payload.
    """
    logger.info(f"Running Performance audit via Lighthouse for {url}")
    
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        report_path = tmp.name
        
    try:
        # Check if lighthouse is available
        subprocess.run(["lighthouse", "--version"], capture_output=True, check=True, text=True)
        
        # Run lighthouse headlessly, targeting performance, and saving as json
        cmd = [
            "lighthouse",
            url,
            "--output=json",
            f"--output-path={report_path}",
            "--chrome-flags=--headless --no-sandbox",
            "--only-categories=performance"
        ]
        subprocess.run(cmd, capture_output=True, check=True, text=True)
        
        with open(report_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        perf_score = data.get("categories", {}).get("performance", {}).get("score", 0)
        metrics = data.get("audits", {})
        
        results = {
            "passed": perf_score >= threshold,
            "score": perf_score * 100,
            "metrics": {
                "lcp": metrics.get("largest-contentful-paint", {}).get("displayValue"),
                "cls": metrics.get("cumulative-layout-shift", {}).get("displayValue"),
                "fcp": metrics.get("first-contentful-paint", {}).get("displayValue"),
                "tti": metrics.get("interactive", {}).get("displayValue")
            }
        }
        return results
        
    except FileNotFoundError:
        logger.warning("Lighthouse CLI not found. Please install via 'npm install -g lighthouse'")
        return {"passed": False, "error": "Lighthouse CLI not installed."}
    except subprocess.CalledProcessError as e:
        logger.error(f"Lighthouse execution failed: {e.stderr}")
        return {"passed": False, "error": "Lighthouse execution failed."}
    except Exception as e:
        logger.error(f"Failed to parse lighthouse report: {e}")
        return {"passed": False, "error": str(e)}
    finally:
        if os.path.exists(report_path):
            os.remove(report_path)
