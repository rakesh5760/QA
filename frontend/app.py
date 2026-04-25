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
        
        # Layout
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.header("📊 Analysis Overview")
            # Backend keys: results["url"], results["page_title"]
            st.subheader(f"Target: {result.get('url', 'Unknown')}")
            st.info(f"Page Title: {result.get('page_title', 'No Title Found')}")
            score_data = result.get("seo_score_data", {})
            total_score = score_data.get("seo_score", 0)
            
            st.write("---")
            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("Overall Score", f"{total_score}/100")
            
            # Use data from new sources
            perf = result.get("performance_metrics", {})
            sec = result.get("security_check", {})
            acc = result.get("accessibility_audit", {})
            
            m2.metric("Technical Score", f"{score_data.get('category_scores', {}).get('technical', 0)}")
            m3.metric("Load Time", f"{perf.get('load_time_s', 0)}s")
            m4.metric("Security", f"✓" if sec.get("is_https") else "✗")
            m5.metric("Access. Score", f"{acc.get('score', 0)}")
            st.write("---")

            tabs = st.tabs(["💡 AI Analysis", "🔍 SEO", "🛡️ Security", "🎨 Accessibility", "🚀 Performance", "❌ Bugs"])
            
            with tabs[0]:
                ai = result.get("ai_insights", {}) or {}
                st.write("### AI Bug Summary")
                st.write(ai.get("bug_summary", "AI analysis unavailable."))
                
                st.write("### 🛠️ Suggested Fixes")
                for fix in ai.get("fix_suggestions", []): st.write(f"- {fix}")

                st.write("### 📝 Functional Test Cases")
                for tc in ai.get("test_cases", []): st.write(f"- {tc}")

                if "form_test_data" in ai:
                    st.write("### 📋 AI Form Lab (Test Data)")
                    form_data = ai["form_test_data"]
                    with st.expander("Show Valid Payloads"):
                        for item in form_data.get("valid", []): st.write(f"- {item.get('field_name')}: `{item.get('value')}`")
                    with st.expander("Show Invalid Payloads"):
                        for item in form_data.get("invalid", []): st.write(f"- {item.get('field_name')}: `{item.get('value')}` ({item.get('reason')})")
                        
            with tabs[1]:
                seo = result.get("seo_analysis", {}) or {}
                st.write(f"**Canonical:** `{seo.get('canonical', 'Missing')}`")
                st.write(f"**Meta Description:** {seo.get('meta_description', 'Missing')}")
                
                st.write("#### Social Meta (Open Graph)")
                sm = seo.get("social_meta", {})
                st.write(f"- **Title:** {sm.get('og:title', 'N/A')}")
                st.write(f"- **Desc:** {sm.get('og:description', 'N/A')}")
                
                st.write("#### Heading Counts")
                h_cols = st.columns(6)
                headings = seo.get("headings", {}) or {}
                for i in range(1, 7): h_cols[i-1].metric(f"H{i}", headings.get(f"h{i}", 0))
                
            with tabs[2]:
                sec = result.get("security_check", {})
                st.write("#### Security Headers")
                if "error" in sec:
                    st.error(sec["error"])
                else:
                    for h, present in sec.get("headers", {}).items():
                        st.write(f"{'✅' if present else '❌'} **{h}**")
                    if sec.get("missing_headers"):
                        st.warning(f"Missing headers: {', '.join(sec['missing_headers'])}")
                    st.write(f"HTTPS Enforced: {'✅' if sec.get('is_https') else '❌'}")
            
            with tabs[3]:
                acc = result.get("accessibility_audit", {})
                if "error" in acc:
                    st.error(acc["error"])
                else:
                    st.metric("Axe Accessibility Score", f"{acc.get('score', 0)}/100")
                    st.write(f"**Passes:** {acc.get('passes_count', 0)} checks")
                    st.write("#### Violations Found")
                    for v in acc.get("violations", []):
                        with st.expander(f"{v['id']} ({v['impact']})"):
                            st.write(f"**{v['description']}**")
                            st.write(f"Affected nodes: {v['nodes_count']}")

            with tabs[4]:
                perf = result.get("performance_metrics", {})
                p1, p2, p3 = st.columns(3)
                p1.metric("TTFB", f"{perf.get('ttfb_ms', 0)}ms")
                p2.metric("FCP", f"{perf.get('fcp_ms', 0)}ms")
                p3.metric("Window Load", f"{perf.get('window_load_ms', 0)}ms")
                
                qa = result.get("qa_checks", {})
                st.write("#### Resource Errors (404s/Failed Load)")
                res_errs = qa.get("resource_errors", [])
                if res_errs:
                    for r in res_errs: st.error(f"{r['resource_type']}: {r['url']} ({r['error']})")
                else:
                    st.success("All resources loaded successfully.")

            with tabs[5]:
                bugs = result.get("bug_report", {}) or {}
                st.metric("Total Links Checked", bugs.get("total_links_checked", 0))
                broken = bugs.get("broken_links", []) or []
                server = bugs.get("server_errors", []) or []
                if broken:
                    st.error(f"Broken Links: {len(broken)}")
                    for b in broken[:15]: st.write(f"- {b['url']} ({b['status_code']})")
                if server:
                    st.warning(f"Server Errors: {len(server)}")
                    for s in server[:15]: st.write(f"- {s['url']} ({s['status_code']})")

        with col2:
            st.header("📸 Screenshot View")
            shots = result.get("screenshots", {})
            if isinstance(shots, dict) and shots:
                bp = st.selectbox("Select Breakpoint", list(shots.keys()))
                path = shots[bp]
                if os.path.exists(path):
                    st.image(path, caption=f"View: {bp}", use_container_width=True)
                else:
                    st.warning(f"File not found: {path}")
            elif result.get("screenshot_path"): # Fallback for old records
                st.image(result["screenshot_path"], use_container_width=True)
            else:
                st.warning("No screenshots available.")

elif menu == "View History":
    st.title("📜 Past Analyses")
    history = get_history()
    
    if history:
        for record in history:
            with st.expander(f"{record['created_at']} - {record['url']}"):
                res = record.get("result", {}) or {}
                
                c1, c2, c3 = st.columns(3)
                bugs_count = len(res.get("bug_report", {}).get("broken_links", []) or [])
                score = res.get("seo_score_data", {}).get("seo_score", "N/A")
                c1.metric("SEO Score", f"{score}/100")
                c2.metric("Broken Links", bugs_count)
                c3.write(f"**Date:** {record['created_at'][:19]}")
                st.info(f"ID: {record['id']}")
                
                st.write("**AI Summary:**")
                st.write(res.get("ai_insights", {}).get("bug_summary", "No summary available"))
                
                if st.button(f"View Full Report for ID {record['id']}"):
                    st.json(res)
    else:
        st.info("No past analyses found. Start a new one!")
