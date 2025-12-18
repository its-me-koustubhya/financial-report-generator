"""
Streamlit Web Interface for Business Report Generator
A user-friendly web UI for generating financial analysis reports
"""

import streamlit as st
import os
from datetime import datetime
from graph.workflow import create_report_workflow
from graph.state import ReportState
from pathlib import Path
import time

# Page configuration
st.set_page_config(
    page_title="AI Financial Report Generator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 3rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .stProgress > div > div > div > div {
        background-color: #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'report_generated' not in st.session_state:
    st.session_state.report_generated = False
if 'final_report' not in st.session_state:
    st.session_state.final_report = ""
if 'report_stats' not in st.session_state:
    st.session_state.report_stats = {}
if 'messages' not in st.session_state:
    st.session_state.messages = []

def save_report_to_file(report: str, company_name: str) -> str:
    """Save report to output directory"""
    os.makedirs("output", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_company_name = company_name.replace(" ", "_").replace("/", "_")
    filename = f"{safe_company_name}_report_{timestamp}.md"
    filepath = os.path.join("output", filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(report)
    
    return filepath

def generate_report_ui(company_name: str, analysis_focus: str = None):
    """Generate report with UI updates"""
    
    # Create workflow
    app = create_report_workflow()
    
    # Initial state
    initial_state = {
        "user_input": company_name,
        "analysis_focus": analysis_focus,
        "raw_data": [],
        "data_sources": [],
        "key_metrics": None,
        "insights": [],
        "trends": [],
        "report_sections": None,
        "final_report": "",
        "current_step": "",
        "messages": [],
        "data_collection_attempts": 0,
        "writing_attempts": 0
    }
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Message container
    message_container = st.container()
    
    try:
        # Update progress
        status_text.text("🔄 Initializing workflow...")
        progress_bar.progress(10)
        time.sleep(0.5)
        
        # Run workflow
        status_text.text("🔍 Collecting data from web sources...")
        progress_bar.progress(25)
        
        result = app.invoke(initial_state)
        
        # Display messages during generation
        with message_container:
            st.subheader("📋 Generation Log")
            for msg in result.get('messages', []):
                if "⚠️" in msg or "WARNING" in msg:
                    st.warning(msg)
                elif "✅" in msg or "PASSED" in msg:
                    st.success(msg)
                elif "🛑" in msg or "FAILED" in msg:
                    st.error(msg)
                else:
                    st.info(msg)
        
        # Update progress
        status_text.text("📊 Analyzing financial data...")
        progress_bar.progress(50)
        time.sleep(0.5)
        
        status_text.text("✍️ Writing report...")
        progress_bar.progress(75)
        time.sleep(0.5)
        
        status_text.text("🎨 Formatting and finalizing...")
        progress_bar.progress(90)
        time.sleep(0.5)
        
        # Complete
        progress_bar.progress(100)
        status_text.text("✅ Report generation complete!")
        
        # Store results in session state
        st.session_state.final_report = result.get('final_report', '')
        st.session_state.report_stats = {
            'data_attempts': result.get('data_collection_attempts', 0),
            'writing_attempts': result.get('writing_attempts', 0),
            'sources': len(result.get('data_sources', [])),
            'length': len(result.get('final_report', '')),
            'status': result.get('current_step', 'unknown')
        }
        st.session_state.messages = result.get('messages', [])
        st.session_state.report_generated = True
        st.session_state.saved_path = save_report_to_file(
          st.session_state.final_report,
          company_name
        )
        
        return True
        
    except Exception as e:
        status_text.text("❌ Error occurred during generation")
        st.error(f"Error: {str(e)}")
        return False

# Main App Layout
def Dashboard():
    # Header
    st.markdown('<h1 class="main-header">📊 AI Financial Report Generator</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Generate comprehensive financial analysis reports using AI-powered Agentic systems</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")

        st.markdown("---")
        
        # Check API keys
        st.subheader("🔑 API Status")
        groq_status = "✅" if os.getenv("GROQ_API_KEY") else "❌"
        tavily_status = "✅" if os.getenv("TAVILY_API_KEY") else "❌"
        
        st.text(f"{groq_status} Groq API")
        st.text(f"{tavily_status} Tavily API")
        
        if not (os.getenv("GROQ_API_KEY") and os.getenv("TAVILY_API_KEY")):
            st.error("⚠️ Please configure API keys in .env file")
        
        st.markdown("---")
        
        st.subheader("📖 About")
        st.info("""
        This tool uses a AI agent system to:
        
        1. 🔍 **Collect** financial data from web sources
        2. 📊 **Analyze** metrics and trends
        3. ✍️ **Write** comprehensive reports
        4. 🎨 **Edit** and format professionally
        
        Built with LangGraph and Groq LLMs.
        """)
        
        st.markdown("---")
        
        st.subheader("🎯 Features")
        st.markdown("""
        - ✅ Real-time progress tracking
        - ✅ Quality validation checks
        - ✅ Automatic retries
        - ✅ Professional formatting
        - ✅ Download reports
        """)
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📝 Report Configuration")
        
        # Input form
        with st.form("report_form"):
            company_name = st.text_input(
                "Company Name *",
                placeholder="e.g., Tesla, Apple Inc, Microsoft",
                help="Enter the full company name you want to analyze"
            )
            
            analysis_focus = st.text_input(
                "Analysis Focus (Optional)",
                placeholder="e.g., Q4 2024 earnings, recent developments",
                help="Specify a particular aspect to focus on"
            )
            
            col_a, col_b, col_c = st.columns([1, 1, 2])
            
            with col_a:
                submit_button = st.form_submit_button(
                    "🚀 Generate Report",
                    use_container_width=True,
                    type="primary"
                )
            
            with col_b:
                clear_button = st.form_submit_button(
                    "🗑️ Clear",
                    use_container_width=True
                )
        
        # Handle form submission
        if submit_button:
            if not company_name:
                st.error("⚠️ Please enter a company name")
            else:
                # Reset state
                st.session_state.report_generated = False
                st.session_state.final_report = ""
                st.session_state.report_stats = {}
                
                # Generate report
                with st.spinner("Generating report..."):
                    success = generate_report_ui(company_name, analysis_focus)
                
                if success:
                    save_report_to_file(
                        st.session_state.final_report,
                        company_name
                    )
                    st.balloons()
                    st.rerun()
        
        if clear_button:
            st.session_state.report_generated = False
            st.session_state.final_report = ""
            st.session_state.report_stats = {}
            st.session_state.messages = []
            st.rerun()
    
    with col2:
        st.subheader("📊 Quick Stats")
        
        if st.session_state.report_generated and st.session_state.report_stats:
            stats = st.session_state.report_stats
            
            # Display metrics
            st.metric("Data Collection Attempts", stats.get('data_attempts', 0))
            st.metric("Writing Attempts", stats.get('writing_attempts', 0))
            st.metric("Sources Collected", stats.get('sources', 0))
            st.metric("Report Length", f"{stats.get('length', 0):,} chars")
            
            # Status badge
            status = stats.get('status', 'unknown')
            if 'early_exit' in status:
                st.error("⚠️ Insufficient Data")
            elif 'writing' in status or 'analysis' in status:
                st.success("✅ Complete")
            else:
                st.info(f"📌 Status: {status}")
        else:
            st.info("Generate a report to see statistics")
    
    # Display report if generated
    if st.session_state.report_generated and st.session_state.final_report:
        st.markdown("---")
        
        col1, col2 = st.columns([4, 1])
        
        with col1:
            st.subheader("📄 Generated Report")
        
        with col2:
            # Download button
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.download_button(
                label="⬇️ Download",
                data=st.session_state.final_report,
                file_name=f"report_{timestamp}.md",
                mime="text/markdown",
                use_container_width=True
            )
        
        # Display report in tabs
        tab1, tab2 = st.tabs(["📖 Formatted View", "📝 Markdown Source"])
        
        with tab1:
            # Render markdown
            st.markdown(st.session_state.final_report)
        
        with tab2:
            # Show raw markdown
            st.code(st.session_state.final_report, language="markdown")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem;'>
        <p>Built with ❤️ using LangGraph, Groq, and Streamlit</p>
        <p style='font-size: 0.9rem;'>
            <a href='https://github.com/its-me-koustubhya/business-report-generator' target='_blank'>GitHub</a>  
        </p>
    </div>
    """, unsafe_allow_html=True)

def load_report_history():
    """Load previously generated reports"""
    output_dir = Path("output")
    if not output_dir.exists():
        return []
    
    reports = []
    for file in output_dir.glob("*.md"):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Extract company name from filename
                company = file.stem.split('_report_')[0].replace('_', ' ')
                reports.append({
                    'filename': file.name,
                    'company': company,
                    'timestamp': datetime.fromtimestamp(file.stat().st_mtime),
                    'size': file.stat().st_size,
                    'content': content
                })
        except Exception:
            continue
    
    return sorted(reports, key=lambda x: x['timestamp'], reverse=True)

def show_history_page():
    """Display report history page"""
    st.subheader("📚 Report History")
    
    reports = load_report_history()
    
    if not reports:
        st.info("No reports generated yet. Create your first report!")
        return
    
    st.write(f"Total reports: **{len(reports)}**")
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        search = st.text_input("🔍 Search by company name", "")
    
    # Filter reports
    if search:
        reports = [r for r in reports if search.lower() in r['company'].lower()]
    
    # Display reports
    for idx, report in enumerate(reports):
        with st.expander(f"📄 {report['company']} - {report['timestamp'].strftime('%Y-%m-%d %H:%M')}"):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.text(f"File: {report['filename']}")
                st.text(f"Size: {report['size']:,} bytes")
            
            with col2:
                if st.button("👁️ View", key=f"view_{idx}"):
                    st.session_state.viewing_report = report
            
            with col3:
                st.download_button(
                    "⬇️ Download",
                    data=report['content'],
                    file_name=report['filename'],
                    mime="text/markdown",
                    key=f"download_{idx}"
                )

def show_comparison_page():
    """Display comparison between reports"""
    st.subheader("📊 Compare Reports")
    
    reports = load_report_history()
    
    if len(reports) < 2:
        st.info("Need at least 2 reports to compare")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        report1 = st.selectbox(
            "Select first report",
            options=reports,
            format_func=lambda x: f"{x['company']} ({x['timestamp'].strftime('%Y-%m-%d')})",
            key="report1"
        )
    
    with col2:
        report2 = st.selectbox(
            "Select second report",
            options=[r for r in reports if r != report1],
            format_func=lambda x: f"{x['company']} ({x['timestamp'].strftime('%Y-%m-%d')})",
            key="report2"
        )
    
    if report1 and report2:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"### {report1['company']}")
            st.markdown(report1['content'][:500] + "...")
        
        with col2:
            st.markdown(f"### {report2['company']}")
            st.markdown(report2['content'][:500] + "...")

def main():
    # Navigation
    page = st.sidebar.radio(
        "📌 Navigation",
        ["🏠 Generate Report", "📚 History", "📊 Compare"]
    )
    
    if page == "🏠 Generate Report":
        Dashboard()
    elif page == "📚 History":
        show_history_page()
    elif page == "📊 Compare":
        show_comparison_page()

if __name__ == "__main__":
    main()