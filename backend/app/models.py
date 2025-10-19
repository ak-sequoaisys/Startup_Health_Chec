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
    EMPLOYMENT_CONTRACTS = "employment_contracts"
    WORKPLACE_SAFETY = "workplace_safety"
    PAYROLL_TAX = "payroll_tax"
    EMPLOYEE_BENEFITS = "employee_benefits"
    WORKPLACE_POLICIES = "workplace_policies"
    RECORD_KEEPING = "record_keeping"
    TERMINATION_PROCEDURES = "termination_procedures"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class QuestionOption(BaseModel):
    id: str
    text: str
    score: int
    risk_level: RiskLevel


class Question(BaseModel):
    id: str
    category: ComplianceCategory
    question_text: str
    question_type: QuestionType
    options: Optional[List[QuestionOption]] = None
    help_text: Optional[str] = None
    weight: int = 1


class Answer(BaseModel):
    question_id: str
    answer_value: str
    score: int


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


class Lead(BaseModel):
    id: str
    company_name: str
    contact_name: str
    email: EmailStr
    phone: Optional[str] = None
    company_size: str
    industry: Optional[str] = None
    submission_date: datetime
    overall_score: int
    overall_risk_level: RiskLevel
    high_risk_categories: List[str]
