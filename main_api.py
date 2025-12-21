from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from graph.workflow import create_report_workflow
from pydantic import BaseModel
from config import settings
import os

app = FastAPI(
    title="Financial Report Generator API",
    description="AI-powered financial report generation using LangGraph",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ReportRequest(BaseModel):
    company_name: str
    analysis_focus: str | None = None

class ReportResponse(BaseModel):
    report: str
    status: str
    company: str

@app.get("/")
def root():
    return {
        "message": "Financial Report Generator API",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "generate_report": "/generate-report (POST)"
        }
    }

@app.get("/health")
def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "groq_key_set": bool(settings.GROQ_API_KEY),
        "tavily_key_set": bool(settings.TAVILY_API_KEY),
        "database_connected": bool(settings.DATABASE_URL)
    }

@app.post("/generate-report", response_model=ReportResponse)
async def generate_report(request: ReportRequest):
    """
    Generate a financial analysis report for a company
    
    - **company_name**: Name of the company to analyze
    - **focus**: Optional specific focus area for the report
    """
    try:
        # Validate API keys are set
        if not settings.GROQ_API_KEY or not settings.TAVILY_API_KEY:
            raise HTTPException(
                status_code=500,
                detail="API keys not configured. Please set GROQ_API_KEY and TAVILY_API_KEY environment variables."
            )
        
        # Create and run workflow
        workflow = create_report_workflow()
        
        initial_state = {
        "user_input": request.company_name,
        "analysis_focus": request.analysis_focus,
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

        # Run the workflow with company name and optional focus
        result = workflow.invoke(initial_state)
        
        # Extract the final report from result
        # Adjust this based on your actual workflow output structure
        final_report = result.get("final_report", "")
        
        if not final_report:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate report. Workflow completed but no report was produced."
            )
        
        return ReportResponse(
            report=final_report,
            status="success",
            company=request.company_name
        )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating report: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)