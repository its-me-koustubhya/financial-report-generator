from typing import Dict
from graph.state import ReportState
from config import llm_precise
from datetime import datetime

def editor_agent(state: ReportState) -> Dict:
    """
    Edits and formats the final report.
    
    Args:
        state: Current report state with draft report
        
    Returns:
        Dict with formatted_report, current_step, and messages
    """
    
    # 1. Get draft report from state
    original_query = state['user_input']
    draft_report = state['final_report']
    
    # 2. Extract clean company name
    search_terms = ["financial", "report", "earnings", "revenue", "profit", "quarterly", "results"]
    words = original_query.split()
    
    # Take words until we hit a search term
    clean_company_parts = []
    for word in words:
        if word.lower() in search_terms:
            break
        clean_company_parts.append(word)
    
    company_name = " ".join(clean_company_parts) if clean_company_parts else words[0]
    
    # 3. Create editing prompt
    prompt = f"""You are a professional editor reviewing a financial analysis report.

Your task: Polish and format this report for final publication.

ORIGINAL REPORT:
{draft_report}

Instructions:
1. Ensure consistent markdown formatting
2. Fix any grammar or clarity issues
3. Improve readability and flow
4. Maintain professional business tone
5. Add proper spacing between sections
6. Ensure all headers use proper markdown (##)
7. Do NOT change the core content or analysis
8. Make sure the company name "{company_name}" is used consistently throughout

Return the polished, final version of the report."""
    
    # 4. Invoke LLM for editing
    response = llm_precise.invoke(prompt)
    
    # 5. Extract final formatted report
    edited_report = response.content.strip()  # Remove any leading/trailing whitespace

    # 6. Create metadata 
    metadata = f"""

---
**Financial Analysis Report**

**Company:** {company_name}

**Generated:** {datetime.now().strftime('%Y-%m-%d')}

**Analysis Period:** 2024

---

"""
    
    formatted_report = metadata + edited_report

    # 7. Return formatted report
    return {
        "final_report": formatted_report,
        "messages": ["Edited report is ready!"]
    }