from typing import Dict
from graph.state import ReportState
from config import get_llm_balanced
import json

def analyst_agent(state: ReportState) -> Dict:
    """
    Analyzes collected data and extracts financial insights.
    
    Args:
        state: Current report state with raw_data
        
    Returns:
        Dict with key_metrics, insights, trends, current_step, and messages
    """
    
    # 1. Get raw data from state
    query = state['user_input']
    raw_data = state.get('raw_data', [])

    # error handling for raw data
    if not raw_data:
        return {
            "key_metrics": {},
            "insights": ["No data available for analysis"],
            "trends": [],
            "current_step": "analysis",
            "messages": ["Warning: No raw data to analyze"]
        }

    # 2. Combine all data chunks
    combined_data = "\n\n".join(raw_data)

    # Limit data size if too large (LLMs have token limits)
    max_chars = 8000  # Adjust based on your needs
    if len(combined_data) > max_chars:
        combined_data = combined_data[:max_chars] + "...[truncated]"

    # 3. Create analysis prompt for LLM
    filter_prompt = f"""Analyze this financial data about {query}:

    {combined_data}

    Return your analysis in this EXACT JSON format:
    {{
      "revenue": "value or unknown",
      "profit": "value or unknown",
      "growth_rate": "value or unknown",
      "key_insights": ["insight1", "insight2", "insight3"],
      "trends": ["trend1", "trend2"]
    }}

    Return ONLY the JSON, no other text."""

    # 4. Invoke LLM to get analysis
    llm_balanced = get_llm_balanced()
    response = llm_balanced.invoke(filter_prompt)
    response_text = response.content

    # Remove markdown code blocks if present
    if "```json" in response_text:
        response_text = response_text.split("```json")[1].split("```")[0]
    elif "```" in response_text:
        response_text = response_text.split("```")[1].split("```")[0]

    response_text = response_text.strip()
    
    # 5. Parse the response into structured format
    try:
      analysis_data = json.loads(response_text)
      
      # Extract the fields
      key_metrics = {
          "revenue": analysis_data.get("revenue", "unknown"),
          "profit": analysis_data.get("profit", "unknown"),
          "growth_rate": analysis_data.get("growth_rate", "unknown")
      }
      
      insights = analysis_data.get("key_insights", [])
      trends = analysis_data.get("trends", [])

      vague_metrics = sum(1 for v in key_metrics.values() 
                       if 'unknown' in str(v).lower() or 'not available' in str(v).lower())
    
        # Create quality-aware message
      if vague_metrics >= 2:
            quality_status = "⚠️ WARNING: Limited data quality"
      else:
            quality_status = "✅ Good data quality"
        
      messages_list = [
            f"Analysis completed. Extracted {len(insights)} insights and {len(trends)} trends",
            f"{quality_status} - {3 - vague_metrics}/3 metrics found, {vague_metrics} unknown"
        ]
    
    except json.JSONDecodeError as e:
        # If JSON parsing fails, return error
        print(f"JSON parsing error: {e}")
        print(f"Response was: {response_text}")
        
        return {
            "key_metrics": {},
            "insights": ["Error: Could not parse analysis results"],
            "trends": [],
            "current_step": "analysis",
            "messages": ["Error: Failed to analyze data properly"]
        }
    
    # 6. Return updated state
    return {
        "key_metrics": key_metrics,
        "insights": insights,
        "trends": trends,
        "current_step": "analysis",
        "messages": messages_list
    }


    