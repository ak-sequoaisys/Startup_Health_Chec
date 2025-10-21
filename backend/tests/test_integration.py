import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import db
from app.models import LeadStatus, RiskLevel

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


class TestFullAssessmentFlow:
    def test_complete_assessment_workflow(self):
        """Test the complete assessment workflow from start to finish"""
        
        start_payload = {
            "email": "integration@example.com",
            "company_name": "Integration Test Company",
            "industry": "Technology",
            "employee_range": "10-50",
            "operating_states": ["NSW", "VIC"],
            "business_age": "1-3 years",
            "consent": True
        }
        
        start_response = client.post("/api/v1/assessments/start", json=start_payload)
        assert start_response.status_code == 200
        lead = start_response.json()
        assessment_id = lead["id"]
        
        assert lead["status"] == LeadStatus.STARTED.value
        assert lead["email"] == start_payload["email"]
        
        questions_response = client.get("/api/v1/questions")
        assert questions_response.status_code == 200
        questions = questions_response.json()
        assert len(questions) > 0
        
        for question in questions:
            if question["options"]:
                answer_payload = {
                    "assessment_id": assessment_id,
                    "question_id": question["id"],
                    "answer_value": question["options"][0]["id"]
                }
                answer_response = client.post("/api/v1/assessments/answer", json=answer_payload)
                assert answer_response.status_code == 200
        
        answers = []
        for question in questions:
            if question["options"]:
                answers.append({
                    "question_id": question["id"],
                    "answer_value": question["options"][0]["id"],
                    "score": question["options"][0]["score"]
                })
        
        submission = {
            "company_name": start_payload["company_name"],
            "contact_name": "Integration Tester",
            "email": start_payload["email"],
            "phone": "1234567890",
            "company_size": start_payload["employee_range"],
            "industry": start_payload["industry"],
            "answers": answers
        }
        
        compute_response = client.post("/api/v1/assessments/compute", json=submission)
        assert compute_response.status_code == 200
        result = compute_response.json()
        
        assert "score" in result
        assert "rating" in result
        assert "gaps" in result
        assert "actions" in result
        assert 0 <= result["score"] <= 100
        assert result["rating"] in [level.value for level in RiskLevel]
        
        assessments_response = client.get("/api/v1/assessments")
        assert assessments_response.status_code == 200
        assessments = assessments_response.json()
        assert len(assessments) > 0
        
        leads_response = client.get("/api/v1/leads")
        assert leads_response.status_code == 200
        leads = leads_response.json()
        assert len(leads) > 0

    def test_multiple_assessments_isolation(self):
        """Test that multiple assessments are properly isolated"""
        
        assessment1_payload = {
            "email": "user1@example.com",
            "company_name": "Company 1",
            "employee_range": "10-50",
            "operating_states": ["NSW"],
            "consent": True
        }
        
        assessment2_payload = {
            "email": "user2@example.com",
            "company_name": "Company 2",
            "employee_range": "50-100",
            "operating_states": ["VIC"],
            "consent": True
        }
        
        response1 = client.post("/api/v1/assessments/start", json=assessment1_payload)
        response2 = client.post("/api/v1/assessments/start", json=assessment2_payload)
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        lead1 = response1.json()
        lead2 = response2.json()
        
        assert lead1["id"] != lead2["id"]
        assert lead1["email"] == assessment1_payload["email"]
        assert lead2["email"] == assessment2_payload["email"]
        
        leads_response = client.get("/api/v1/leads")
        leads = leads_response.json()
        assert len(leads) >= 2

    def test_assessment_with_different_risk_levels(self):
        """Test assessment scoring produces different risk levels"""
        questions = client.get("/api/v1/questions").json()
        
        high_score_answers = []
        for question in questions:
            if question["options"]:
                best_option = max(question["options"], key=lambda x: x["score"])
                high_score_answers.append({
                    "question_id": question["id"],
                    "answer_value": best_option["id"],
                    "score": best_option["score"]
                })
        
        high_score_submission = {
            "company_name": "High Score Company",
            "contact_name": "High Scorer",
            "email": "highscore@example.com",
            "company_size": "10-50",
            "answers": high_score_answers
        }
        
        high_response = client.post("/api/v1/assessments/compute", json=high_score_submission)
        assert high_response.status_code == 200
        high_result = high_response.json()
        
        low_score_answers = []
        for question in questions:
            if question["options"]:
                worst_option = min(question["options"], key=lambda x: x["score"])
                low_score_answers.append({
                    "question_id": question["id"],
                    "answer_value": worst_option["id"],
                    "score": worst_option["score"]
                })
        
        low_score_submission = {
            "company_name": "Low Score Company",
            "contact_name": "Low Scorer",
            "email": "lowscore@example.com",
            "company_size": "10-50",
            "answers": low_score_answers
        }
        
        low_response = client.post("/api/v1/assessments/compute", json=low_score_submission)
        assert low_response.status_code == 200
        low_result = low_response.json()
        
        assert high_result["score"] > low_result["score"]
        assert len(low_result["gaps"]) >= len(high_result["gaps"])

    def test_answer_update_workflow(self):
        """Test updating answers during assessment"""
        
        start_payload = {
            "email": "update@example.com",
            "company_name": "Update Test Company",
            "employee_range": "10-50",
            "operating_states": ["NSW"],
            "consent": True
        }
        
        start_response = client.post("/api/v1/assessments/start", json=start_payload)
        assessment_id = start_response.json()["id"]
        
        questions = client.get("/api/v1/questions").json()
        first_question = questions[0]
        
        initial_answer = {
            "assessment_id": assessment_id,
            "question_id": first_question["id"],
            "answer_value": first_question["options"][0]["id"]
        }
        
        response1 = client.post("/api/v1/assessments/answer", json=initial_answer)
        assert response1.status_code == 200
        assert response1.json()["answers_count"] == 1
        
        updated_answer = {
            "assessment_id": assessment_id,
            "question_id": first_question["id"],
            "answer_value": first_question["options"][1]["id"]
        }
        
        response2 = client.post("/api/v1/assessments/answer", json=updated_answer)
        assert response2.status_code == 200
        assert response2.json()["answers_count"] == 1
        
        second_question = questions[1]
        new_answer = {
            "assessment_id": assessment_id,
            "question_id": second_question["id"],
            "answer_value": second_question["options"][0]["id"]
        }
        
        response3 = client.post("/api/v1/assessments/answer", json=new_answer)
        assert response3.status_code == 200
        assert response3.json()["answers_count"] == 2

    def test_category_scoring_accuracy(self):
        """Test that category scores are calculated correctly"""
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
            "company_name": "Category Test Company",
            "contact_name": "Category Tester",
            "email": "category@example.com",
            "company_size": "10-50",
            "answers": answers
        }
        
        response = client.post("/api/v1/assessments", json=submission)
        assert response.status_code == 200
        result = response.json()
        
        assert "category_scores" in result
        category_scores = result["category_scores"]
        
        for cat_score in category_scores:
            assert "category" in cat_score
            assert "score" in cat_score
            assert "max_score" in cat_score
            assert "percentage" in cat_score
            assert "risk_level" in cat_score
            assert "issues" in cat_score
            assert "recommendations" in cat_score
            
            assert cat_score["score"] <= cat_score["max_score"]
            assert 0 <= cat_score["percentage"] <= 100
            
            expected_percentage = (cat_score["score"] / cat_score["max_score"]) * 100 if cat_score["max_score"] > 0 else 0
            assert abs(cat_score["percentage"] - expected_percentage) < 0.01

    def test_priority_actions_generation(self):
        """Test that priority actions are generated based on risk"""
        questions = client.get("/api/v1/questions").json()
        
        answers = []
        for question in questions:
            if question["options"]:
                worst_option = min(question["options"], key=lambda x: x["score"])
                answers.append({
                    "question_id": question["id"],
                    "answer_value": worst_option["id"],
                    "score": worst_option["score"]
                })
        
        submission = {
            "company_name": "Priority Test Company",
            "contact_name": "Priority Tester",
            "email": "priority@example.com",
            "company_size": "10-50",
            "answers": answers
        }
        
        response = client.post("/api/v1/assessments", json=submission)
        assert response.status_code == 200
        result = response.json()
        
        assert "priority_actions" in result
        assert isinstance(result["priority_actions"], list)
        assert len(result["priority_actions"]) > 0
