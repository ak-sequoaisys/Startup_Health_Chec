from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from datetime import datetime
import hashlib
import uuid
from app.models import Question, AssessmentSubmission, AssessmentResult, Lead, StartAssessmentRequest, LeadStatus, AnswerRequest, InProgressAssessment, Answer
from app.questions_data import get_all_questions, get_question_by_id
from app.assessment_service import calculate_assessment_result, create_lead_from_submission
from app.database import db

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
