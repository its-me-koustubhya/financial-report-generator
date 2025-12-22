from langgraph.graph import StateGraph, START, END
from graph.state import ReportState
from agents.data_collector import data_collector_agent
from agents.analyst import analyst_agent
from agents.writer import writer_agent
from agents.editor import editor_agent
from agents.quality_checker import (
    check_analysis_quality,
    check_report_quality,
    retry_data_collection,
    retry_writing,
    handle_insufficient_data  
)

def create_report_workflow(groq_api_key: str = None, tavily_api_key: str = None):
    """
    Creates the LangGraph workflow with quality checks and early exit.

    Create workflow with optional user API keys.
    If not provided, uses server's default keys.
    """
    
    workflow = StateGraph(ReportState)
    
    # Store keys in workflow config to pass to agents
    workflow.config = {
        "groq_api_key": groq_api_key,
        "tavily_api_key": tavily_api_key
    }
    
    # Add all nodes
    workflow.add_node("data_collector", data_collector_agent)
    workflow.add_node("analyst", analyst_agent)
    workflow.add_node("writer", writer_agent)
    workflow.add_node("editor", editor_agent)
    workflow.add_node("retry_data_collection", retry_data_collection)
    workflow.add_node("retry_writing", retry_writing)
    workflow.add_node("insufficient_data_handler", handle_insufficient_data) 
    
    # Edges
    workflow.add_edge(START, "data_collector")
    workflow.add_edge("data_collector", "analyst")
    
    # CONDITIONAL: After analyst - now with 3 options!
    workflow.add_conditional_edges(
        "analyst",
        check_analysis_quality,
        {
            "proceed_to_writer": "writer",
            "collect_more_data": "retry_data_collection",
            "insufficient_data": "insufficient_data_handler" 
        }
    )
    
    workflow.add_edge("retry_data_collection", "data_collector")
    
    # Early exit goes straight to END
    workflow.add_edge("insufficient_data_handler", END)
    
    # Rest of workflow continues as before
    workflow.add_edge("writer", "editor")
    
    workflow.add_conditional_edges(
        "editor",
        check_report_quality,
        {
            "finalize": END,
            "revise_report": "retry_writing"
        }
    )
    
    workflow.add_edge("retry_writing", "writer")
    
    app = workflow.compile()
    return app

