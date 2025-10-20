from typing import List, Dict
from datetime import datetime
import uuid
from app.models import (
    AssessmentSubmission, AssessmentResult, CategoryScore, 
    RiskLevel, ComplianceCategory, Lead, Answer, CATEGORY_WEIGHTS
)
from app.questions_data import get_all_questions, get_question_by_id


def calculate_risk_level(percentage: float) -> RiskLevel:
    if percentage >= 71:
        return RiskLevel.HEALTHY
    elif percentage >= 41:
        return RiskLevel.MODERATE
    else:
        return RiskLevel.HIGH_RISK


def get_category_recommendations(category: ComplianceCategory, score: int, max_score: int) -> List[str]:
    percentage = (score / max_score * 100) if max_score > 0 else 0
    
    recommendations = {
        ComplianceCategory.REGISTRATION: [
            "Ensure business registration is up to date with all relevant authorities",
            "Verify all required licenses and permits are current",
            "Register for all applicable tax obligations",
            "Maintain proper business structure documentation"
        ],
        ComplianceCategory.EMPLOYEE_DOCS: [
            "Review and update all employment contracts to ensure they include mandatory clauses",
            "Ensure all new hires receive written contracts before starting work",
            "Document all leave entitlements and policies",
            "Implement a contract management system to track renewals and updates"
        ],
        ComplianceCategory.PAYROLL_STATUTORY: [
            "Register for PAYG withholding if not already done",
            "Implement Single Touch Payroll (STP) reporting",
            "Ensure superannuation contributions are made on time for all eligible employees",
            "Engage a qualified accountant or payroll specialist"
        ],
        ComplianceCategory.WORKPLACE_POLICIES: [
            "Develop comprehensive workplace policies covering all key areas",
            "Develop and document a comprehensive WHS policy",
            "Ensure all policies are communicated to employees",
            "Provide training on key policies (e.g., anti-discrimination, harassment)"
        ],
        ComplianceCategory.LABOUR_FILINGS: [
            "Document clear termination and redundancy procedures",
            "Ensure all terminations follow proper legal processes",
            "Provide training to managers on termination procedures",
            "Maintain records of all labour-related filings and submissions"
        ],
        ComplianceCategory.GOVERNANCE: [
            "Implement a robust record-keeping system",
            "Ensure all employee records are complete and up-to-date",
            "Train HR staff on record-keeping requirements",
            "Conduct regular audits of employee records"
        ]
    }
    
    category_recs = recommendations.get(category, [])
    
    if percentage >= 71:
        return [category_recs[0]] if category_recs else []
    elif percentage >= 41:
        return category_recs[:2] if len(category_recs) >= 2 else category_recs
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
                if option and option.risk_level in [RiskLevel.HIGH_RISK, RiskLevel.MODERATE]:
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
    overall_weighted_score = 0
    overall_max_weighted_score = 0
    
    for category, data in category_data.items():
        if data["max_score"] > 0:
            category_percentage = (data["score"] / data["max_score"]) * 100
            risk_level = calculate_risk_level(category_percentage)
            issues = get_category_issues(category, data["answers"])
            recommendations = get_category_recommendations(category, data["score"], data["max_score"])
            
            category_weight = CATEGORY_WEIGHTS.get(category, 0)
            weighted_score = (category_percentage / 100) * category_weight
            
            category_scores.append(CategoryScore(
                category=category,
                score=data["score"],
                max_score=data["max_score"],
                percentage=round(category_percentage, 2),
                risk_level=risk_level,
                issues=issues,
                recommendations=recommendations
            ))
            
            overall_weighted_score += weighted_score
            overall_max_weighted_score += category_weight
    
    overall_percentage = (overall_weighted_score / overall_max_weighted_score * 100) if overall_max_weighted_score > 0 else 0
    overall_risk_level = calculate_risk_level(overall_percentage)
    
    priority_actions = []
    high_risk_categories = [cs for cs in category_scores if cs.risk_level == RiskLevel.HIGH_RISK]
    moderate_categories = [cs for cs in category_scores if cs.risk_level == RiskLevel.MODERATE]
    
    for cat_score in high_risk_categories[:3]:
        if cat_score.recommendations:
            priority_actions.append(f"HIGH RISK - {cat_score.category.value}: {cat_score.recommendations[0]}")
    
    for cat_score in moderate_categories[:2]:
        if cat_score.recommendations and len(priority_actions) < 5:
            priority_actions.append(f"MODERATE - {cat_score.category.value}: {cat_score.recommendations[0]}")
    
    if not priority_actions:
        priority_actions.append("Continue maintaining your current compliance standards")
        priority_actions.append("Consider periodic reviews to ensure ongoing compliance")
    
    result = AssessmentResult(
        id=str(uuid.uuid4()),
        submission_date=datetime.now(),
        company_name=submission.company_name,
        contact_name=submission.contact_name,
        email=submission.email,
        overall_score=int(overall_weighted_score),
        max_score=int(overall_max_weighted_score),
        overall_percentage=round(overall_percentage, 2),
        overall_risk_level=overall_risk_level,
        category_scores=category_scores,
        priority_actions=priority_actions
    )
    
    return result


def create_lead_from_submission(submission: AssessmentSubmission, result: AssessmentResult) -> Lead:
    high_risk_categories = [
        cs.category.value for cs in result.category_scores 
        if cs.risk_level in [RiskLevel.HIGH_RISK, RiskLevel.MODERATE]
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
