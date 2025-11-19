from typing import TypedDict, List, Dict, Optional, Annotated
import operator

class ReportState(TypedDict):
  """state for report generator agent"""
  
  user_input: str #contain company name or topic
  analysis_focus: Optional[str] # specific aspects

  raw_data: Annotated[List[str], operator.add] #  Accumulate data chunks
  data_sources: Annotated[List[str], operator.add]  #Track URLs/sources

  key_metrics: Optional[Dict] # Financial metrics found (revenue, profit, etc.)
  insights: Annotated[List[str], operator.add] # Key findings
  trends: Annotated[List[str], operator.add] # Identified trends

  report_sections: Optional[Dict[str, str]] # Different sections (intro, analysis, conclusion)
  final_report: str # polished report

  current_step: str # Track which agent is working
  messages: Annotated[List, operator.add] #Status messages

  data_collection_attempts: int  # Track retry attempts
  writing_attempts: int  # Track writing retry attempts
