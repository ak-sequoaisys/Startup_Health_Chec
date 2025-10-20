from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from typing import List, Optional
from datetime import datetime
import hashlib
import uuid
from app.models import Question, AssessmentSubmission, AssessmentResult, Lead, StartAssessmentRequest, LeadStatus, AnswerRequest, InProgressAssessment, Answer, AuditLog
from app.questions_data import get_all_questions, get_question_by_id
from app.assessment_service import calculate_assessment_result, create_lead_from_submission
from app.database import db
from app.pdf_service import generate_pdf_report
from app.email_service import email_service
from app.admin_models import TrialRecord, TrialFilters
from app.admin_service import get_trials, export_trials_csv
from app.auth import get_current_user

app = FastAPI(title="Startup Compliance Health Check API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


@app.post("/api/v1/assessments/start", response_model=Lead)
async def start_assessment(request: Request, data: StartAssessmentRequest):
    try:
        client_ip = request.client.host if request.client else "unknown"
        ip_hash = hashlib.sha256(client_ip.encode()).hexdigest()
        
        user_agent = request.headers.get("user-agent", "unknown")
        
        lead = Lead(
            id=str(uuid.uuid4()),
            company_name=data.company_name,
            contact_name="",
            email=data.email,
            company_size=data.employee_range,
            industry=data.industry,
            employee_range=data.employee_range,
            operating_states=data.operating_states,
            business_age=data.business_age,
            consent=data.consent,
            status=LeadStatus.STARTED,
            ip_hash=ip_hash,
            user_agent=user_agent,
            submission_date=datetime.now(),
        )
        
        db.save_lead(lead)
        
        return lead
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting assessment: {str(e)}")


@app.get("/api/v1/questions", response_model=List[Question])
async def get_questions():
    return get_all_questions()


@app.get("/api/v1/questions/{question_id}", response_model=Question)
async def get_question(question_id: str):
    question = get_question_by_id(question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question


@app.post("/api/v1/assessments/answer")
async def submit_answer(answer_request: AnswerRequest):
    try:
        question = get_question_by_id(answer_request.question_id)
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        in_progress = db.get_in_progress_assessment(answer_request.assessment_id)
        if not in_progress:
            lead = db.get_lead(answer_request.assessment_id)
            if not lead:
                raise HTTPException(status_code=404, detail="Assessment not found")
            
            in_progress = InProgressAssessment(
                id=answer_request.assessment_id,
                lead_id=answer_request.assessment_id,
                answers=[],
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        
        score = 0
        if question.options:
            option = next((opt for opt in question.options if opt.id == answer_request.answer_value), None)
            if option:
                score = option.score
        
        existing_answer_idx = next((i for i, ans in enumerate(in_progress.answers) if ans.question_id == answer_request.question_id), None)
        new_answer = Answer(
            question_id=answer_request.question_id,
            answer_value=answer_request.answer_value,
            score=score
        )
        
        if existing_answer_idx is not None:
            in_progress.answers[existing_answer_idx] = new_answer
        else:
            in_progress.answers.append(new_answer)
        
        in_progress.updated_at = datetime.now()
        db.save_in_progress_assessment(in_progress)
        
        return {"status": "success", "answers_count": len(in_progress.answers)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving answer: {str(e)}")


@app.post("/api/v1/assessments", response_model=AssessmentResult)
async def submit_assessment(submission: AssessmentSubmission):
    try:
        result = calculate_assessment_result(submission)
        
        db.save_assessment(result)
        
        lead = create_lead_from_submission(submission, result)
        db.save_lead(lead)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing assessment: {str(e)}")


@app.post("/api/v1/assessments/compute")
async def compute_assessment(submission: AssessmentSubmission):
    try:
        result = calculate_assessment_result(submission)
        
        db.save_assessment(result)
        
        lead = create_lead_from_submission(submission, result)
        db.save_lead(lead)
        
        try:
            email_service.send_notification(result)
        except Exception as email_error:
            print(f"Failed to send email notification: {email_error}")
        
        gaps = []
        for cat_score in result.category_scores:
            if cat_score.issues:
                for issue in cat_score.issues:
                    gaps.append({
                        "category": cat_score.category.value,
                        "issue": issue,
                        "risk_level": cat_score.risk_level.value
                    })
        
        actions = result.priority_actions
        
        return {
            "score": result.overall_percentage,
            "rating": result.overall_risk_level.value,
            "gaps": gaps,
            "actions": actions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error computing assessment: {str(e)}")


@app.get("/api/v1/assessments/{assessment_id}", response_model=AssessmentResult)
async def get_assessment(assessment_id: str):
    assessment = db.get_assessment(assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return assessment


@app.get("/api/v1/assessments", response_model=List[AssessmentResult])
async def get_all_assessments():
    return db.get_all_assessments()


@app.get("/api/v1/leads", response_model=List[Lead])
async def get_leads():
    return db.get_all_leads()


@app.get("/api/v1/leads/{lead_id}", response_model=Lead)
async def get_lead(lead_id: str):
    lead = db.get_lead(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@app.post("/api/v1/reports/generate")
async def generate_report(assessment_id: str):
    try:
        assessment = db.get_assessment(assessment_id)
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        pdf_path = generate_pdf_report(assessment)
        
        return FileResponse(
            path=pdf_path,
            media_type="application/pdf",
            filename=f"compliance_report_{assessment.company_name.replace(' ', '_')}_{assessment.submission_date.strftime('%Y%m%d')}.pdf"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")


@app.get("/api/v1/audit-logs", response_model=List[AuditLog])
async def get_audit_logs():
    return db.get_all_audit_logs()


@app.get("/api/v1/audit-logs/{audit_log_id}", response_model=AuditLog)
async def get_audit_log(audit_log_id: str):
    audit_log = db.get_audit_log(audit_log_id)
    if not audit_log:
        raise HTTPException(status_code=404, detail="Audit log not found")
    return audit_log


@app.get("/api/v1/admin/trials", response_model=List[TrialRecord])
async def get_admin_trials(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    states: Optional[str] = None,
    score_min: Optional[float] = None,
    score_max: Optional[float] = None,
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    try:
        filters = None
        if any([start_date, end_date, states, score_min, score_max, status]):
            filters = TrialFilters(
                start_date=datetime.fromisoformat(start_date) if start_date else None,
                end_date=datetime.fromisoformat(end_date) if end_date else None,
                states=states.split(",") if states else None,
                score_min=score_min,
                score_max=score_max,
                status=LeadStatus(status) if status else None
            )
        
        trials = get_trials(filters)
        return trials
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching trials: {str(e)}")


@app.get("/api/v1/admin/trials/export")
async def export_admin_trials(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    states: Optional[str] = None,
    score_min: Optional[float] = None,
    score_max: Optional[float] = None,
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    try:
        filters = None
        if any([start_date, end_date, states, score_min, score_max, status]):
            filters = TrialFilters(
                start_date=datetime.fromisoformat(start_date) if start_date else None,
                end_date=datetime.fromisoformat(end_date) if end_date else None,
                states=states.split(",") if states else None,
                score_min=score_min,
                score_max=score_max,
                status=LeadStatus(status) if status else None
            )
        
        trials = get_trials(filters)
        csv_content = export_trials_csv(trials)
        
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=trials_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting trials: {str(e)}")
