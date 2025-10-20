from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum


class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    YES_NO = "yes_no"
    TEXT = "text"
    NUMBER = "number"


class ComplianceCategory(str, Enum):
    REGISTRATION = "registration"
    EMPLOYEE_DOCS = "employee_docs"
    PAYROLL_STATUTORY = "payroll_statutory"
    WORKPLACE_POLICIES = "workplace_policies"
    LABOUR_FILINGS = "labour_filings"
    GOVERNANCE = "governance"


CATEGORY_WEIGHTS = {
    ComplianceCategory.REGISTRATION: 20,
    ComplianceCategory.EMPLOYEE_DOCS: 15,
    ComplianceCategory.PAYROLL_STATUTORY: 25,
    ComplianceCategory.WORKPLACE_POLICIES: 15,
    ComplianceCategory.LABOUR_FILINGS: 20,
    ComplianceCategory.GOVERNANCE: 5,
}


class RiskLevel(str, Enum):
    HEALTHY = "healthy"
    MODERATE = "moderate"
    HIGH_RISK = "high_risk"


class QuestionOption(BaseModel):
    id: str
    text: str
    score: int
    risk_level: RiskLevel


class ApplicabilityRule(BaseModel):
    rule_type: str
    threshold: Optional[int] = None
    states: Optional[List[str]] = None


class GovernmentSource(BaseModel):
    name: str
    url: str
    description: Optional[str] = None


class Question(BaseModel):
    id: str
    category: ComplianceCategory
    question_text: str
    question_type: QuestionType
    options: Optional[List[QuestionOption]] = None
    help_text: Optional[str] = None
    weight: int = 1
    applicability_rules: Optional[List[ApplicabilityRule]] = None
    government_sources: Optional[List[GovernmentSource]] = None


class Answer(BaseModel):
    question_id: str
    answer_value: str
    score: int


class AnswerRequest(BaseModel):
    assessment_id: str
    question_id: str
    answer_value: str


class InProgressAssessment(BaseModel):
    id: str
    lead_id: str
    answers: List[Answer]
    created_at: datetime
    updated_at: datetime


class AssessmentSubmission(BaseModel):
    company_name: str
    contact_name: str
    email: EmailStr
    phone: Optional[str] = None
    company_size: str
    industry: Optional[str] = None
    answers: List[Answer]


class CategoryScore(BaseModel):
    category: ComplianceCategory
    score: int
    max_score: int
    percentage: float
    risk_level: RiskLevel
    issues: List[str]
    recommendations: List[str]


class AssessmentResult(BaseModel):
    id: str
    submission_date: datetime
    company_name: str
    contact_name: str
    email: EmailStr
    overall_score: int
    max_score: int
    overall_percentage: float
    overall_risk_level: RiskLevel
    category_scores: List[CategoryScore]
    priority_actions: List[str]


class LeadStatus(str, Enum):
    STARTED = "started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class StartAssessmentRequest(BaseModel):
    email: EmailStr
    company_name: str
    industry: Optional[str] = None
    employee_range: str
    operating_states: List[str]
    business_age: Optional[str] = None
    consent: bool


class Lead(BaseModel):
    id: str
    company_name: str
    contact_name: str
    email: EmailStr
    phone: Optional[str] = None
    company_size: str
    industry: Optional[str] = None
    employee_range: Optional[str] = None
    operating_states: Optional[List[str]] = None
    business_age: Optional[str] = None
    consent: bool = False
    status: LeadStatus = LeadStatus.STARTED
    ip_hash: Optional[str] = None
    user_agent: Optional[str] = None
    submission_date: datetime
    overall_score: Optional[int] = None
    overall_risk_level: Optional[RiskLevel] = None
    high_risk_categories: Optional[List[str]] = None
