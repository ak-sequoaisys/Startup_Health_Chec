import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from app.main import app
from app.database import db
from app.models import (
    ComplianceCategory,
    RiskLevel,
    LeadStatus,
)

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_database():
    """Reset database before each test"""
    db.assessments = {}
    db.leads = {}
    db.in_progress_assessments = {}
    db.audit_logs = {}
    yield
    db.assessments = {}
    db.leads = {}
    db.in_progress_assessments = {}
    db.audit_logs = {}


class TestHealthCheck:
    def test_healthz_endpoint(self):
        """Test health check endpoint returns ok status"""
        response = client.get("/healthz")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestQuestionsEndpoints:
    def test_get_all_questions(self):
        """Test retrieving all questions"""
        response = client.get("/api/v1/questions")
        assert response.status_code == 200
        questions = response.json()
        assert isinstance(questions, list)
        assert len(questions) > 0
        
        first_question = questions[0]
        assert "id" in first_question
        assert "category" in first_question
        assert "question_text" in first_question
        assert "question_type" in first_question
        assert "weight" in first_question

    def test_get_question_by_id(self):
        """Test retrieving a specific question by ID"""
        all_questions = client.get("/api/v1/questions").json()
        question_id = all_questions[0]["id"]
        
        response = client.get(f"/api/v1/questions/{question_id}")
        assert response.status_code == 200
        question = response.json()
        assert question["id"] == question_id

    def test_get_nonexistent_question(self):
        """Test retrieving a non-existent question returns 404"""
        response = client.get("/api/v1/questions/nonexistent-id")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestStartAssessment:
    def test_start_assessment_success(self):
        """Test starting a new assessment"""
        payload = {
            "email": "test@example.com",
            "company_name": "Test Company",
            "industry": "Technology",
            "employee_range": "10-50",
            "operating_states": ["NSW", "VIC"],
            "business_age": "1-3 years",
            "consent": True
        }
        
        response = client.post("/api/v1/assessments/start", json=payload)
        assert response.status_code == 200
        lead = response.json()
        
        assert lead["email"] == payload["email"]
        assert lead["company_name"] == payload["company_name"]
        assert lead["industry"] == payload["industry"]
        assert lead["employee_range"] == payload["employee_range"]
        assert lead["operating_states"] == payload["operating_states"]
        assert lead["status"] == LeadStatus.STARTED.value
        assert "id" in lead
        assert "ip_hash" in lead
        assert "submission_date" in lead

    def test_start_assessment_invalid_email(self):
        """Test starting assessment with invalid email"""
        payload = {
            "email": "invalid-email",
            "company_name": "Test Company",
            "employee_range": "10-50",
            "operating_states": ["NSW"],
            "consent": True
        }
        
        response = client.post("/api/v1/assessments/start", json=payload)
        assert response.status_code == 422


class TestAnswerSubmission:
    def test_submit_answer_new_assessment(self):
        """Test submitting an answer for a new assessment"""
        start_payload = {
            "email": "test@example.com",
            "company_name": "Test Company",
            "employee_range": "10-50",
            "operating_states": ["NSW"],
            "consent": True
        }
        start_response = client.post("/api/v1/assessments/start", json=start_payload)
        assessment_id = start_response.json()["id"]
        
        questions = client.get("/api/v1/questions").json()
        first_question = questions[0]
        
        answer_payload = {
            "assessment_id": assessment_id,
            "question_id": first_question["id"],
            "answer_value": first_question["options"][0]["id"]
        }
        
        response = client.post("/api/v1/assessments/answer", json=answer_payload)
        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "success"
        assert result["answers_count"] == 1

    def test_submit_answer_update_existing(self):
        """Test updating an existing answer"""
        start_payload = {
            "email": "test@example.com",
            "company_name": "Test Company",
            "employee_range": "10-50",
            "operating_states": ["NSW"],
            "consent": True
        }
        start_response = client.post("/api/v1/assessments/start", json=start_payload)
        assessment_id = start_response.json()["id"]
        
        questions = client.get("/api/v1/questions").json()
        first_question = questions[0]
        
        answer_payload = {
            "assessment_id": assessment_id,
            "question_id": first_question["id"],
            "answer_value": first_question["options"][0]["id"]
        }
        
        client.post("/api/v1/assessments/answer", json=answer_payload)
        
        answer_payload["answer_value"] = first_question["options"][1]["id"]
        response = client.post("/api/v1/assessments/answer", json=answer_payload)
        
        assert response.status_code == 200
        result = response.json()
        assert result["answers_count"] == 1

    def test_submit_answer_invalid_question(self):
        """Test submitting answer for non-existent question"""
        start_payload = {
            "email": "test@example.com",
            "company_name": "Test Company",
            "employee_range": "10-50",
            "operating_states": ["NSW"],
            "consent": True
        }
        start_response = client.post("/api/v1/assessments/start", json=start_payload)
        assessment_id = start_response.json()["id"]
        
        answer_payload = {
            "assessment_id": assessment_id,
            "question_id": "invalid-question-id",
            "answer_value": "some-answer"
        }
        
        response = client.post("/api/v1/assessments/answer", json=answer_payload)
        assert response.status_code == 404


class TestAssessmentSubmission:
    def test_submit_complete_assessment(self):
        """Test submitting a complete assessment"""
        questions = client.get("/api/v1/questions").json()
        
        answers = []
        for question in questions:
            if question["options"]:
                answers.append({
                    "question_id": question["id"],
                    "answer_value": question["options"][0]["id"],
                    "score": question["options"][0]["score"]
                })
        
        submission = {
            "company_name": "Test Company",
            "contact_name": "John Doe",
            "email": "john@example.com",
            "phone": "1234567890",
            "company_size": "10-50",
            "industry": "Technology",
            "answers": answers
        }
        
        response = client.post("/api/v1/assessments", json=submission)
        assert response.status_code == 200
        result = response.json()
        
        assert "id" in result
        assert result["company_name"] == submission["company_name"]
        assert result["email"] == submission["email"]
        assert "overall_score" in result
        assert "overall_percentage" in result
        assert "overall_risk_level" in result
        assert "category_scores" in result
        assert "priority_actions" in result
        assert len(result["category_scores"]) > 0

    def test_compute_assessment_endpoint(self):
        """Test compute assessment endpoint"""
        questions = client.get("/api/v1/questions").json()
        
        answers = []
        for question in questions:
            if question["options"]:
                answers.append({
                    "question_id": question["id"],
                    "answer_value": question["options"][0]["id"],
                    "score": question["options"][0]["score"]
                })
        
        submission = {
            "company_name": "Test Company",
            "contact_name": "John Doe",
            "email": "john@example.com",
            "company_size": "10-50",
            "answers": answers
        }
        
        response = client.post("/api/v1/assessments/compute", json=submission)
        assert response.status_code == 200
        result = response.json()
        
        assert "score" in result
        assert "rating" in result
        assert "gaps" in result
        assert "actions" in result
        assert isinstance(result["gaps"], list)
        assert isinstance(result["actions"], list)


class TestAssessmentRetrieval:
    def test_get_assessment_by_id(self):
        """Test retrieving an assessment by ID"""
        questions = client.get("/api/v1/questions").json()
        
        answers = []
        for question in questions:
            if question["options"]:
                answers.append({
                    "question_id": question["id"],
                    "answer_value": question["options"][0]["id"],
                    "score": question["options"][0]["score"]
                })
        
        submission = {
            "company_name": "Test Company",
            "contact_name": "John Doe",
            "email": "john@example.com",
            "company_size": "10-50",
            "answers": answers
        }
        
        create_response = client.post("/api/v1/assessments", json=submission)
        assessment_id = create_response.json()["id"]
        
        response = client.get(f"/api/v1/assessments/{assessment_id}")
        assert response.status_code == 200
        assessment = response.json()
        assert assessment["id"] == assessment_id

    def test_get_nonexistent_assessment(self):
        """Test retrieving non-existent assessment returns 404"""
        response = client.get("/api/v1/assessments/nonexistent-id")
        assert response.status_code == 404

    def test_get_all_assessments(self):
        """Test retrieving all assessments"""
        response = client.get("/api/v1/assessments")
        assert response.status_code == 200
        assessments = response.json()
        assert isinstance(assessments, list)


class TestLeadsEndpoints:
    def test_get_all_leads(self):
        """Test retrieving all leads"""
        response = client.get("/api/v1/leads")
        assert response.status_code == 200
        leads = response.json()
        assert isinstance(leads, list)

    def test_get_lead_by_id(self):
        """Test retrieving a lead by ID"""
        start_payload = {
            "email": "test@example.com",
            "company_name": "Test Company",
            "employee_range": "10-50",
            "operating_states": ["NSW"],
            "consent": True
        }
        start_response = client.post("/api/v1/assessments/start", json=start_payload)
        lead_id = start_response.json()["id"]
        
        response = client.get(f"/api/v1/leads/{lead_id}")
        assert response.status_code == 200
        lead = response.json()
        assert lead["id"] == lead_id

    def test_get_nonexistent_lead(self):
        """Test retrieving non-existent lead returns 404"""
        response = client.get("/api/v1/leads/nonexistent-id")
        assert response.status_code == 404


class TestAuditLogs:
    def test_get_all_audit_logs(self):
        """Test retrieving all audit logs"""
        response = client.get("/api/v1/audit-logs")
        assert response.status_code == 200
        logs = response.json()
        assert isinstance(logs, list)

    def test_get_audit_log_by_id_not_found(self):
        """Test retrieving non-existent audit log"""
        response = client.get("/api/v1/audit-logs/nonexistent-id")
        assert response.status_code == 404
