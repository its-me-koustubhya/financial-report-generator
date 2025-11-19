from typing import Dict
from graph.state import ReportState
from config import llm_creative

def format_list_items(items, prefix=""):
    """Helper to format list items"""
    return "\n".join([f"{prefix}- {item}" for item in items])

def writer_agent(state: ReportState) -> Dict:
    """
    Writes a structured financial report from analyzed data.
    
    Args:
        state: Current report state with analysis results
        
    Returns:
        Dict with report_sections, current_step, and messages
    """
    
    # 1. Extract all necessary data from state
    company = state['user_input']
    metrics = state['key_metrics']
    insights = state['insights']
    trends = state['trends']
    sources = state.get('data_sources', [])

    # After extracting from state
    if not metrics or not insights:
        return {
            "final_report": "",
            "current_step": "writing",
            "messages": ["Error: Missing analysis data for report generation"]
        }
    
    # 2. Create comprehensive writing prompt
    prompt = f"""You are a senior financial analyst writing an executive report about {company}.

    Based on this analysis data:

    FINANCIAL METRICS:
    - Revenue: {metrics.get('revenue', 'Not available')}
    - Profit: {metrics.get('profit', 'Not available')}
    - Growth Rate: {metrics.get('growth_rate', 'Not available')}

    KEY INSIGHTS:
    {format_list_items(insights)}

    MARKET TRENDS:
    {format_list_items(trends)}

    Write a comprehensive financial analysis report with the following sections:
    

    1. **Executive Summary** (2-3 paragraphs)
      - Brief overview of company's financial position
      - Highlight the most important metrics and findings
      - Provide a snapshot of overall performance

    2. **Company Overview** (1-2 paragraphs)
      - Brief company background and industry context
      - Core business model and revenue streams

    3. **Financial Performance Analysis** (3-4 paragraphs)
      - Detailed analysis of revenue, profit, and growth metrics
      - Break down performance by business segments if available
      - Compare current performance to historical trends
      - Discuss factors driving financial results
      - Include a brief metrics summary table using markdown tables

    4. **Market Position & Competitive Landscape** (2-3 paragraphs)
      - Company's position in the industry
      - Competitive advantages and challenges
      - Market trends affecting the company
      - Strategic initiatives and their impact

    5. **Key Insights & Strategic Observations** (2-3 paragraphs)
      - Most important takeaways from the analysis
      - Strategic implications of current trends
      - Potential risks and opportunities
      - Write in flowing paragraphs, not bullet points
      - Create a brief bullet list of top 3 risks and top 3 opportunities

    6. **Conclusion** (1-2 paragraphs)
      - Overall assessment of financial health and trajectory
      - Forward-looking predictions based on current trends
      - Key risks and opportunities summary
      - Specific areas stakeholders should monitor
      - Final strategic recommendation or outlook

    IMPORTANT GUIDELINES:
    - Write in a professional, analytical tone
    - Use specific numbers and data points from the metrics
    - Use **bold** for key metrics and important findings
    - Use *italic* for emphasis on critical points
    - Avoid repeating the same phrases across sections
    - Use varied language to express similar concepts
    - Avoid repetition between sections
    - Each section should flow naturally into the next
    - Focus on ANALYSIS and INTERPRETATION, not just stating facts
    - Use markdown formatting with ## for section headers
    - Write in complete paragraphs - avoid excessive bullet points
    - Aim for depth and insight, not just surface-level summary
    - Total report should be comprehensive (2000-3000 words)

    Generate the complete report now.
    
    DATA SOURCES:
    {format_list_items(sources[:10])} 

    Reference these sources appropriately in your analysis where relevant."""
    
    # 3. Invoke LLM to generate report
    report = llm_creative.invoke(prompt)

    complete_report_text = report.content
    
    # 5. Return report sections or complete report
    return {
    "final_report": complete_report_text,
    "current_step": "writing",
    "messages": ["Report written successfully"]
    }

if __name__ == "__main__":
    test_state = {
        "user_input": "Tesla",
        "key_metrics": {
            "revenue": "$96.8 billion (2023)",
            "profit": "$15 billion net income",
            "growth_rate": "19% YoY revenue growth"
        },
        "insights": [
            "Strong revenue growth driven by vehicle deliveries",
            "Improving profit margins due to operational efficiency"
        ],
        "trends": [
            "Expanding production capacity globally",
            "Stock price appreciation of 120% YoY"
        ]
    }
    
    result = writer_agent(test_state)
    print("Report Generated:")
    print("="*50)
    print(result['final_report'])
    print("="*50)
    print(f"Status: {result['messages']}")