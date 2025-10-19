from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from app.models import Question, AssessmentSubmission, AssessmentResult, Lead
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


@app.get("/api/questions", response_model=List[Question])
async def get_questions():
    return get_all_questions()


@app.get("/api/questions/{question_id}", response_model=Question)
async def get_question(question_id: str):
    question = get_question_by_id(question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question


@app.post("/api/assessments", response_model=AssessmentResult)
async def submit_assessment(submission: AssessmentSubmission):
    try:
        result = calculate_assessment_result(submission)
        
        db.save_assessment(result)
        
        lead = create_lead_from_submission(submission, result)
        db.save_lead(lead)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing assessment: {str(e)}")


@app.get("/api/assessments/{assessment_id}", response_model=AssessmentResult)
async def get_assessment(assessment_id: str):
    assessment = db.get_assessment(assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return assessment


@app.get("/api/assessments", response_model=List[AssessmentResult])
async def get_all_assessments():
    return db.get_all_assessments()


@app.get("/api/leads", response_model=List[Lead])
async def get_leads():
    return db.get_all_leads()


@app.get("/api/leads/{lead_id}", response_model=Lead)
async def get_lead(lead_id: str):
    lead = db.get_lead(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead
