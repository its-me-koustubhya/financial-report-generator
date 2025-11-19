from typing import Dict, Literal
from graph.state import ReportState
from datetime import datetime

def check_analysis_quality(state: ReportState) -> Literal["proceed_to_writer", "collect_more_data", "insufficient_data"]:
    """
    Checks if the analysis has sufficient quality to proceed to writing.
    
    Args:
        state: Current report state
        
    Returns:
        "proceed_to_writer" if quality is good
        "collect_more_data" if needs retry (and under max attempts)
        "insufficient_data" if max retries exhausted with poor quality
    """
    
    # Get analysis results
    key_metrics = state.get('key_metrics', {})
    insights = state.get('insights', [])
    trends = state.get('trends', [])
    raw_data = state.get('raw_data', [])
    attempts = state.get('data_collection_attempts', 0)
    
    # Quality criteria
    issues = []
    
    # Check 1: Unknown or vague metrics
    vague_keywords = ['unknown', 'not available', 'not disclosed', 'estimated', 'not found', 'no data']
    
    vague_metrics = 0
    for key, value in key_metrics.items():
        value_lower = str(value).lower()
        if any(keyword in value_lower for keyword in vague_keywords):
            vague_metrics += 1
    
    if vague_metrics >= 2:
        issues.append(f"Too many vague/unknown metrics: {vague_metrics}/3")
    
    # Check 2: Insufficient insights (be stricter)
    if len(insights) < 3:
        issues.append(f"Insufficient insights: {len(insights)} (need at least 3)")
    
    # Check 3: Insights are too generic/short
    generic_insights = sum(1 for insight in insights if len(insight) < 30)
    if generic_insights > len(insights) / 2:
        issues.append(f"Insights too generic/short: {generic_insights}/{len(insights)}")
    
    # Check 4: Insufficient trends
    if len(trends) < 3:
        issues.append(f"Insufficient trends: {len(trends)} (need at least 3)")
    
    # Check 5: Not enough raw data collected
    if len(raw_data) < 5:
        issues.append(f"Insufficient raw data: {len(raw_data)} chunks (need at least 5)")
    
    # Check 6: Raw data is too short (likely poor quality results)
    total_chars = sum(len(chunk) for chunk in raw_data)
    if total_chars < 2000:
        issues.append(f"Raw data too short: {total_chars} chars (need at least 2000)")
    
    # Check 7: Company name appears in data (validates relevance)
    company_name = state.get('user_input', '').split()[0]  # First word
    company_mentions = sum(1 for chunk in raw_data if company_name.lower() in chunk.lower())
    if company_mentions < 2:
        issues.append(f"Company barely mentioned in data: {company_mentions} times")
    
    # Make decision
    if issues and attempts < 2:  # Allow retry if under max attempts
        print(f"\n⚠️  QUALITY CHECK FAILED - Analysis Quality Issues:")
        for issue in issues:
            print(f"   - {issue}")
        print(f"   → Routing back to data collection (attempt {attempts + 1})\n")
        return "collect_more_data"
    elif issues and attempts >= 2:
        # Max retries reached with poor quality - STOP HERE!
        print(f"\n🛑 CRITICAL: Quality issues persist after max retries:")
        for issue in issues:
            print(f"   - {issue}")
        print(f"   → Routing to early exit (insufficient data)\n")
        return "insufficient_data"
    else:
        print(f"\n✅ QUALITY CHECK PASSED - Analysis quality is sufficient")
        print(f"   - Known metrics: {3 - vague_metrics}/3")
        print(f"   - Insights: {len(insights)}")
        print(f"   - Trends: {len(trends)}")
        print(f"   - Raw data: {len(raw_data)} chunks ({total_chars} chars)")
        print(f"   - Company mentions: {company_mentions}")
        print(f"   → Proceeding to writer\n")
        return "proceed_to_writer"


def check_report_quality(state: ReportState) -> Literal["finalize", "revise_report"]:
    """
    Checks if the final report meets quality standards.
    
    Args:
        state: Current report state
        
    Returns:
        "finalize" if report is good, "revise_report" if needs revision
    """
    
    final_report = state.get('final_report', '')
    attempts = state.get('writing_attempts', 0)
    
    # Get ORIGINAL company name (clean it)
    original_query = state.get('user_input', '')
    search_terms = ["financial", "report", "earnings", "revenue", "profit", "quarterly", "results"]
    words = original_query.split()
    
    # Extract just company name
    clean_company_parts = []
    for word in words:
        if word.lower() in search_terms:
            break
        clean_company_parts.append(word)
    
    company_name = " ".join(clean_company_parts) if clean_company_parts else words[0]
    
    # Quality criteria
    issues = []
    
    # Check 1: Report length (should be substantial)
    MIN_LENGTH = 3000
    if len(final_report) < MIN_LENGTH:
        issues.append(f"Report too short: {len(final_report)} chars (minimum {MIN_LENGTH})")
    
    # Check 2: Has all major sections
    required_sections = [
        "Executive Summary",
        "Company Overview", 
        "Financial Performance",
        "Market Position",
        "Key Insights",
        "Conclusion"
    ]
    
    missing_sections = [section for section in required_sections if section not in final_report]
    if missing_sections:
        issues.append(f"Missing sections: {', '.join(missing_sections)}")
    
    # Check 3: Too many vague/placeholder terms
    vague_terms = ['unknown', 'not available', 'not disclosed', 'not found', 'no data', 'estimated']
    vague_count = sum(final_report.lower().count(term) for term in vague_terms)
    if vague_count > 5:
        issues.append(f"Too many vague terms: {vague_count} instances")
    
    # Check 4: Company is actually discussed
    company_base = company_name.split()[0].lower()
    report_lower = final_report.lower()
    
    # Count all variations
    company_mentions = (
        report_lower.count(company_base) +
        report_lower.count(f"{company_base}'s") +
        report_lower.count(f"{company_base} inc")
    )
    
    # Subtract metadata mentions (appears in header)
    company_mentions = max(0, company_mentions - 2)
    
    if company_mentions < 10:
        issues.append(f"Company barely discussed: mentioned only {company_mentions} times (found '{company_base}' and variations)")
    
    # Check 5: Has specific numbers/data points
    # Count occurrences of $ or % or numbers with B/M/K (billion/million/thousand)
    import re
    numbers = len(re.findall(r'\$[\d,]+\.?\d*[BMK]?|\d+\.?\d*%', final_report))
    if numbers < 5:
        issues.append(f"Lacks specific data points: only {numbers} quantitative metrics")
    
    # Check 6: Not mostly empty/template
    if len(final_report.strip()) < 500:
        issues.append("Report is essentially empty")
    
    # Make decision
    if issues and attempts < 2:
        print(f"\n⚠️  QUALITY CHECK FAILED - Report Quality Issues:")
        for issue in issues:
            print(f"   - {issue}")
        print(f"   → Routing back to writer (attempt {attempts + 1})\n")
        return "revise_report"
    elif issues and attempts >= 2:
        print(f"\n⚠️  Quality issues detected but max retries reached:")
        for issue in issues:
            print(f"   - {issue}")
        print(f"   → Finalizing report with disclaimer\n")
        return "finalize"
    else:
        print(f"\n✅ QUALITY CHECK PASSED - Report meets quality standards")
        print(f"   - Length: {len(final_report)} chars")
        print(f"   - All sections present: Yes")
        print(f"   - Vague terms: {vague_count}")
        print(f"   - Company mentions: {company_mentions}")
        print(f"   - Quantitative data: {numbers} metrics")
        print(f"   → Finalizing report\n")
        return "finalize"


def retry_data_collection(state: ReportState) -> Dict:
    """
    Prepares state for retrying data collection with enhanced queries.
    """
    attempts = state.get('data_collection_attempts', 0) + 1
    original_query = state['user_input']
    
    print(f"\n🔄 RETRY #{attempts} - Enhancing data collection strategy...")
    
    # For retry, add more specific financial search terms
    enhanced_focus = f"{original_query} financial report earnings revenue profit quarterly results 2024 2023"
    
    return {
        "user_input": enhanced_focus,
        "data_collection_attempts": attempts,
        "messages": [f"Retrying data collection (attempt {attempts}) with enhanced search terms"]
    }


def retry_writing(state: ReportState) -> Dict:
    """
    Prepares state for retrying report writing with more detail.
    """
    attempts = state.get('writing_attempts', 0) + 1
    
    print(f"\n🔄 RETRY #{attempts} - Attempting to improve report quality...")
    
    return {
        "writing_attempts": attempts,
        "messages": [f"Retrying report generation (attempt {attempts}) with focus on more detail and specifics"]
    }

def handle_insufficient_data(state: ReportState) -> Dict:
    """
    Handles cases where sufficient data cannot be collected.
    Creates a minimal report explaining the issue.
    """
    company = state['user_input']
    attempts = state.get('data_collection_attempts', 0)
    
    # Create a simple disclaimer report instead of full analysis
    disclaimer_report = f"""---
    **Financial Analysis Report**
    **Company:** {company.split()[0]}
    **Generated:** {datetime.now().strftime('%Y-%m-%d')}
    **Status:** Insufficient Data Available
    ---

    ## Data Collection Notice

    After {attempts} attempts to gather financial information about **{company.split()[0]}**, we were unable to find sufficient publicly available data to generate a comprehensive financial analysis report.

    ### Possible Reasons:
    - The company may be privately held with limited public disclosures
    - The company name may be misspelled or not widely recognized
    - The company may be very small or newly established
    - The company may not exist or may have recently ceased operations

    ### Recommendation:
    Please verify:
    1. The correct company name and spelling
    2. Whether the company is publicly traded or has public financial disclosures
    3. Alternative names or variations the company might use
    4. Whether you meant to search for a different, similarly-named company

    If you believe this is an error, please try again with more specific details such as:
    - Full legal company name
    - Stock ticker symbol (if publicly traded)
    - Industry or business type
    - Geographic location

    ---
    *This report was generated automatically after failing to collect sufficient data for analysis.*
"""
    
    print(f"\n🛑 EARLY EXIT - Insufficient data to continue")
    print(f"   Creating disclaimer report instead of full analysis")
    print(f"   This saves resources and provides better user experience\n")
    
    return {
        "final_report": disclaimer_report,
        "current_step": "early_exit",
        "messages": [f"Insufficient data found after {attempts} attempts. Created disclaimer report."]
    }