from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from database.connection import get_db, SessionLocal
from database.models import User, Report
from auth.dependencies import get_current_user
from pydantic import BaseModel
from datetime import datetime
from graph.workflow import create_report_workflow

router = APIRouter(prefix="/reports", tags=["Reports"])

class ReportRequest(BaseModel):
    user_input: str
    analysis_focus: str | None = None

class ReportResponse(BaseModel):
    id: int
    company_name: str
    focus: str | None
    report_content: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

def process_report_background(
    report_id: int,
    company_name: str,
    focus: str,
    groq_api_key: str,
    tavily_api_key: str
):
    """
    Background task that generates the report.
    Runs in a separate thread, doesn't block the API response.
    """
    db = SessionLocal()
    
    try:
        report = db.query(Report).filter(Report.id == report_id).first()
        
        if not report:
            print(f"Error: Report {report_id} not found")
            return
        
        # Generate the report
        workflow = create_report_workflow(
            groq_api_key=groq_api_key,
            tavily_api_key=tavily_api_key
        )
        
        result = workflow.invoke({
            "user_input": company_name,
            "analysis_focus": focus or "",
        })
        
        final_report = result.get("final_report", "")
        
        if not final_report:
            raise Exception("Workflow completed but no report was produced")
        
        # Update with success
        report.report_content = final_report
        report.status = "success"
        db.commit()
        
        print(f"✅ Report {report_id} completed successfully")
        
    except Exception as e:
        print(f"❌ Error generating report {report_id}: {str(e)}")
        
        report = db.query(Report).filter(Report.id == report_id).first()
        if report:
            report.status = "failed"
            report.report_content = f"Error: {str(e)}"
            db.commit()
    
    finally:
        db.close()

@router.post("/generate", response_model=ReportResponse, status_code=202)
async def generate_report(
    request: ReportRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a financial analysis report for a company (async processing).
    
    Requires:
    - Authentication (Bearer token)
    - User must have configured Groq and Tavily API keys
    
    - **company_name**: Name of the company to analyze
    - **focus**: Optional specific focus area for the report
    """
    # Check if user has API keys configured
    if not current_user.groq_api_key or not current_user.tavily_api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please configure your API keys first using PUT /auth/api-keys"
        )
    
    # Create a pending report entry
    new_report = Report(
        user_id=current_user.id,
        company_name=request.user_input,
        focus=request.analysis_focus,
        report_content="Report is being generated. Please check back in a moment.",
        status="pending"
    )
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    
    # Start background processing
    background_tasks.add_task(
        process_report_background,
        new_report.id,
        request.user_input,
        request.analysis_focus,
        current_user.groq_api_key,
        current_user.tavily_api_key
    )
    
    # Return immediately
    return new_report

@router.get("/stats", response_model=dict)
def get_report_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get statistics about user's reports.
    
    Returns:
        - total_reports: Total number of reports generated
        - successful: Number of successful reports
        - failed: Number of failed reports
        - pending: Number of reports still processing
    """
    from sqlalchemy import func
    
    stats = db.query(
        func.count(Report.id).label('total'),
        func.sum(func.case((Report.status == 'success', 1), else_=0)).label('successful'),
        func.sum(func.case((Report.status == 'failed', 1), else_=0)).label('failed'),
        func.sum(func.case((Report.status == 'pending', 1), else_=0)).label('pending')
    ).filter(Report.user_id == current_user.id).first()
    
    return {
        "total_reports": stats.total or 0,
        "successful": stats.successful or 0,
        "failed": stats.failed or 0,
        "pending": stats.pending or 0
    }

@router.get("/", response_model=List[ReportResponse])
def get_my_reports(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10
):
    """
    Get all reports generated by the current user.
    
    - **skip**: Number of reports to skip (for pagination)
    - **limit**: Maximum number of reports to return (default 10, max 50)
    """
    if limit > 50:
        limit = 50
    
    reports = db.query(Report)\
        .filter(Report.user_id == current_user.id)\
        .order_by(Report.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return reports

@router.get("/{report_id}", response_model=ReportResponse)
def get_report_status(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get report status and content.
    
    Status values:
    - 'pending': Still generating
    - 'success': Completed successfully
    - 'failed': Generation failed
    """
    report = db.query(Report)\
        .filter(Report.id == report_id, Report.user_id == current_user.id)\
        .first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report {report_id} not found"
        )
    
    return report

@router.get("/{report_id}", response_model=ReportResponse)
def get_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific report by ID.
    
    Can only access your own reports.
    """
    report = db.query(Report)\
        .filter(Report.id == report_id, Report.user_id == current_user.id)\
        .first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    return report

@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a report by ID.
    
    Can only delete your own reports.
    """
    report = db.query(Report)\
        .filter(Report.id == report_id, Report.user_id == current_user.id)\
        .first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    db.delete(report)
    db.commit()
    
    return None