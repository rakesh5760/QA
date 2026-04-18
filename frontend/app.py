import streamlit as st
import requests
import json
import os
from datetime import datetime

# Page Configuration
st.set_page_config(
    page_title="AI Intelligent QA Automation",
    page_icon="🤖",
    layout="wide"
)

# Constants
BACKEND_URL = "http://127.0.0.1:8000"

def run_analysis(url):
    try:
        response = requests.post(f"{BACKEND_URL}/analyze-basic", json={"url": url}, timeout=150)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 422:
            st.error("Invalid URL format. Please enter a full URL (e.g., https://google.com)")
        else:
            st.error(f"Backend Error: {response.status_code}")
    except Exception as e:
        st.error(f"Connection Failed: Could not connect to backend at {BACKEND_URL}")
    return None

def get_history():
    try:
        response = requests.get(f"{BACKEND_URL}/history")
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Failed to fetch history.")
    return []

# Session State for persistence
if "last_result" not in st.session_state:
    st.session_state.last_result = None

# Sidebar Navigation
st.sidebar.title("🔍 QA Dashboard")
menu = st.sidebar.radio("Navigation", ["Run New Analysis", "View History"])

if menu == "Run New Analysis":
    st.title("🚀 AI-Powered QA Automation")
    st.markdown("Enter a website URL to perform automated SEO auditing, bug detection, and AI insights.")

    url_input = st.text_input("Website URL", placeholder="https://example.com", key="analyze_url")
    
    if st.button("Start Analysis", type="primary"):
        if url_input and (url_input.startswith("http://") or url_input.startswith("https://")):
            with st.spinner("🕷️ Crawling website and generating AI insights..."):
                result = run_analysis(url_input)
                if result:
                    st.session_state.last_result = result
                    st.success("Analysis Complete!")
                else:
                    st.session_state.last_result = None
        else:
            st.warning("Please enter a valid URL including http:// or https://")

    # Display results if they exist in state
    if st.session_state.last_result:
        result = st.session_state.last_result
        
        # DEBUG: Show raw data if needed
        with st.sidebar.expander("🛠️ Raw Data Debug"):
            st.json(result)
        
        # Layout
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.header("📊 Analysis Overview")
            # Backend keys: results["url"], results["page_title"]
            st.subheader(f"Target: {result.get('url', 'Unknown')}")
            st.info(f"Page Title: {result.get('page_title', 'No Title Found')}")
            
            tabs = st.tabs(["💡 AI Insights", "🔍 SEO Analysis", "❌ Bug Report"])
            
            with tabs[0]:
                ai = result.get("ai_insights", {}) or {}
                st.write("### AI Bug Summary")
                st.write(ai.get("bug_summary", "AI analysis unavailable."))
                
                st.write("### 🛠️ Suggested Fixes")
                fixes = ai.get("fix_suggestions", []) or []
                if not fixes: st.write("No suggestions available.")
                for fix in fixes:
                    if isinstance(fix, dict):
                        st.write(f"- **{fix.get('description', 'Fix')}**")
                    else:
                        st.write(f"- {fix}")
                
                st.write("### 📝 Functional Test Cases")
                tcs = ai.get("test_cases", []) or []
                if not tcs: st.write("No test cases generated.")
                for tc in tcs:
                    if isinstance(tc, dict):
                        st.write(f"- **{tc.get('name', 'Test Case')}**: {tc.get('expected_result', 'N/A')}")
                    else:
                        st.write(f"- {tc}")
                        
            with tabs[1]:
                seo = result.get("seo_analysis", {}) or {}
                st.write(f"**Meta Description:** {seo.get('meta_description', 'Missing')}")
                
                st.write("#### Heading Counts")
                h_cols = st.columns(6)
                # Backend key: results["seo_analysis"]["headings"] (dict with h1, h2, etc.)
                headings = seo.get("headings", {}) or {}
                for i in range(1, 7):
                    count = headings.get(f"h{i}", 0)
                    h_cols[i-1].metric(f"H{i}", count)
                    
                st.write("#### Image Issues")
                img_total = seo.get("total_images", 0)
                img_missing = seo.get("images_missing_alt", 0)
                st.metric("Images without Alt Text", f"{img_missing}/{img_total}", delta=img_missing, delta_color="inverse")
                
            with tabs[2]:
                bugs = result.get("bug_report", {}) or {}
                st.metric("Total Links Checked", bugs.get("total_links_checked", 0))
                
                c1, c2 = st.columns(2)
                broken = bugs.get("broken_links", []) or []
                server = bugs.get("server_errors", []) or []
                
                c1.error(f"Broken Links (4xx): {len(broken)}")
                if broken:
                    for b in broken[:10]:
                        url_val = b.get('url', 'N/A') if isinstance(b, dict) else str(b)
                        st.write(f"- {url_val}")
                                
                c2.warning(f"Server Errors (5xx): {len(server)}")
                if server:
                    for s in server[:10]:
                        url_val = s.get('url', 'N/A') if isinstance(s, dict) else str(s)
                        st.write(f"- {url_val}")

        with col2:
            st.header("📸 Screenshot")
            screenshot_path = result.get("screenshot_path")
            if screenshot_path:
                # Normalize path separators for the current OS
                clean_path = screenshot_path.replace("\\", "/").replace("//", "/")
                # Ensure we have the base screenshots/ directory
                if os.path.exists(clean_path):
                    st.image(clean_path, use_container_width=True)
                else:
                    # Try relative to current wd
                    alt_path = os.path.basename(clean_path)
                    if os.path.exists(f"screenshots/{alt_path}"):
                        st.image(f"screenshots/{alt_path}", use_container_width=True)
                    else:
                        st.warning(f"Screenshot not found: {clean_path}")
            else:
                st.warning("No screenshot available.")

elif menu == "View History":
    st.title("📜 Past Analyses")
    history = get_history()
    
    if history:
        for record in history:
            with st.expander(f"{record['created_at']} - {record['url']}"):
                res = record.get("result", {}) or {}
                
                c1, c2, c3 = st.columns(3)
                bugs_count = len(res.get("bug_report", {}).get("broken_links", []) or [])
                c1.metric("Broken Links", bugs_count)
                c2.info(f"ID: {record['id']}")
                c3.write(f"**Date:** {record['created_at'][:19]}")
                
                st.write("**AI Summary:**")
                st.write(res.get("ai_insights", {}).get("bug_summary", "No summary available"))
                
                if st.button(f"View Full Report for ID {record['id']}"):
                    st.json(res)
    else:
        st.info("No past analyses found. Start a new one!")
