from typing import List, Dict
from datetime import datetime
import uuid
from app.models import (
    AssessmentSubmission, AssessmentResult, CategoryScore, 
    RiskLevel, ComplianceCategory, Lead, Answer
)
from app.questions_data import get_all_questions, get_question_by_id


def calculate_risk_level(percentage: float) -> RiskLevel:
    if percentage >= 80:
        return RiskLevel.LOW
    elif percentage >= 60:
        return RiskLevel.MEDIUM
    elif percentage >= 40:
        return RiskLevel.HIGH
    else:
        return RiskLevel.CRITICAL


def get_category_recommendations(category: ComplianceCategory, score: int, max_score: int) -> List[str]:
    percentage = (score / max_score * 100) if max_score > 0 else 0
    
    recommendations = {
        ComplianceCategory.EMPLOYMENT_CONTRACTS: [
            "Review and update all employment contracts to ensure they include mandatory clauses",
            "Ensure all new hires receive written contracts before starting work",
            "Consider having contracts reviewed by an employment lawyer",
            "Implement a contract management system to track renewals and updates"
        ],
        ComplianceCategory.WORKPLACE_SAFETY: [
            "Develop and document a comprehensive WHS policy",
            "Conduct regular workplace safety inspections (at least quarterly)",
            "Provide safety training to all employees",
            "Establish an incident reporting and investigation process"
        ],
        ComplianceCategory.PAYROLL_TAX: [
            "Register for PAYG withholding if not already done",
            "Implement Single Touch Payroll (STP) reporting",
            "Engage a qualified accountant or payroll specialist",
            "Conduct a payroll audit to ensure compliance"
        ],
        ComplianceCategory.EMPLOYEE_BENEFITS: [
            "Ensure superannuation contributions are made on time for all eligible employees",
            "Review and document all leave entitlements",
            "Implement a leave management system",
            "Conduct regular audits of employee benefits"
        ],
        ComplianceCategory.WORKPLACE_POLICIES: [
            "Develop comprehensive workplace policies covering all key areas",
            "Ensure all policies are communicated to employees",
            "Provide training on key policies (e.g., anti-discrimination, harassment)",
            "Review and update policies annually"
        ],
        ComplianceCategory.RECORD_KEEPING: [
            "Implement a robust record-keeping system",
            "Ensure all employee records are complete and up-to-date",
            "Train HR staff on record-keeping requirements",
            "Conduct regular audits of employee records"
        ],
        ComplianceCategory.TERMINATION_PROCEDURES: [
            "Document clear termination and redundancy procedures",
            "Ensure all terminations follow proper legal processes",
            "Provide training to managers on termination procedures",
            "Consider legal review before any termination"
        ]
    }
    
    category_recs = recommendations.get(category, [])
    
    if percentage >= 80:
        return [category_recs[0]] if category_recs else []
    elif percentage >= 60:
        return category_recs[:2] if len(category_recs) >= 2 else category_recs
    elif percentage >= 40:
        return category_recs[:3] if len(category_recs) >= 3 else category_recs
    else:
        return category_recs


def get_category_issues(category: ComplianceCategory, answers: List[Answer]) -> List[str]:
    issues = []
    questions = get_all_questions()
    
    for answer in answers:
        question = get_question_by_id(answer.question_id)
        if question and question.category == category:
            if answer.score < 10:
                option = next((opt for opt in question.options if opt.id == answer.answer_value), None)
                if option and option.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                    issues.append(f"{question.question_text}: {option.text}")
    
    return issues


def calculate_assessment_result(submission: AssessmentSubmission) -> AssessmentResult:
    questions = get_all_questions()
    
    category_data: Dict[ComplianceCategory, Dict] = {}
    for category in ComplianceCategory:
        category_data[category] = {
            "score": 0,
            "max_score": 0,
            "answers": []
        }
    
    for answer in submission.answers:
        question = get_question_by_id(answer.question_id)
        if question:
            category = question.category
            weighted_score = answer.score * question.weight
            weighted_max = 10 * question.weight
            
            category_data[category]["score"] += weighted_score
            category_data[category]["max_score"] += weighted_max
            category_data[category]["answers"].append(answer)
    
    category_scores = []
    overall_score = 0
    overall_max_score = 0
    
    for category, data in category_data.items():
        if data["max_score"] > 0:
            percentage = (data["score"] / data["max_score"]) * 100
            risk_level = calculate_risk_level(percentage)
            issues = get_category_issues(category, data["answers"])
            recommendations = get_category_recommendations(category, data["score"], data["max_score"])
            
            category_scores.append(CategoryScore(
                category=category,
                score=data["score"],
                max_score=data["max_score"],
                percentage=round(percentage, 2),
                risk_level=risk_level,
                issues=issues,
                recommendations=recommendations
            ))
            
            overall_score += data["score"]
            overall_max_score += data["max_score"]
    
    overall_percentage = (overall_score / overall_max_score * 100) if overall_max_score > 0 else 0
    overall_risk_level = calculate_risk_level(overall_percentage)
    
    priority_actions = []
    critical_categories = [cs for cs in category_scores if cs.risk_level == RiskLevel.CRITICAL]
    high_categories = [cs for cs in category_scores if cs.risk_level == RiskLevel.HIGH]
    
    for cat_score in critical_categories[:3]:
        if cat_score.recommendations:
            priority_actions.append(f"CRITICAL - {cat_score.category.value}: {cat_score.recommendations[0]}")
    
    for cat_score in high_categories[:2]:
        if cat_score.recommendations and len(priority_actions) < 5:
            priority_actions.append(f"HIGH - {cat_score.category.value}: {cat_score.recommendations[0]}")
    
    if not priority_actions:
        priority_actions.append("Continue maintaining your current compliance standards")
        priority_actions.append("Consider periodic reviews to ensure ongoing compliance")
    
    result = AssessmentResult(
        id=str(uuid.uuid4()),
        submission_date=datetime.now(),
        company_name=submission.company_name,
        contact_name=submission.contact_name,
        email=submission.email,
        overall_score=overall_score,
        max_score=overall_max_score,
        overall_percentage=round(overall_percentage, 2),
        overall_risk_level=overall_risk_level,
        category_scores=category_scores,
        priority_actions=priority_actions
    )
    
    return result


def create_lead_from_submission(submission: AssessmentSubmission, result: AssessmentResult) -> Lead:
    high_risk_categories = [
        cs.category.value for cs in result.category_scores 
        if cs.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
    ]
    
    lead = Lead(
        id=result.id,
        company_name=submission.company_name,
        contact_name=submission.contact_name,
        email=submission.email,
        phone=submission.phone,
        company_size=submission.company_size,
        industry=submission.industry,
        submission_date=result.submission_date,
        overall_score=result.overall_score,
        overall_risk_level=result.overall_risk_level,
        high_risk_categories=high_risk_categories
    )
    
    return lead
