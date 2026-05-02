import logging
import language_tool_python

logger = logging.getLogger(__name__)

# Cache the tool instance to avoid recreation overhead
_tool = None

def get_language_tool():
    global _tool
    if _tool is None:
        # Use public API to avoid heavy local java server download
        # Note: Public API has rate limits
        _tool = language_tool_python.LanguageToolPublicAPI('en-US')
    return _tool

async def run_spelling_audit(page):
    """
    Extracts text from the page and runs a spelling/grammar check using LanguageTool.
    """
    logger.info("Running Spelling & Grammar audit")
    try:
        # Extract visible text, ignoring scripts and styles
        text = await page.evaluate('''() => {
            const elements = document.querySelectorAll('body *:not(script):not(style)');
            let content = '';
            for (const el of elements) {
                // Get direct text node children
                for (const node of el.childNodes) {
                    if (node.nodeType === 3) {
                        content += node.nodeValue.trim() + ' ';
                    }
                }
            }
            return content.replace(/\s+/g, ' ').trim();
        }''')
        
        # Limit text to 2000 chars to avoid API rate limits/costs
        text = text[:2000]
        if not text:
            return {"passed": True, "issues": []}
            
        tool = get_language_tool()
        matches = tool.check(text)
        
        issues = []
        for match in matches:
            issues.append({
                "message": match.message,
                "context": match.context,
                "replacements": match.replacements[:3] # Top 3 suggestions
            })
            
        return {
            "passed": len(issues) == 0,
            "issue_count": len(issues),
            "issues": issues
        }
    except Exception as e:
        logger.error(f"Failed to run spelling audit: {e}")
        return {"passed": False, "error": str(e)}
