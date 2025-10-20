import os
from typing import Dict, List, Optional
from datetime import datetime
from app.models import AssessmentResult, Lead, InProgressAssessment

try:
    from sqlalchemy import create_engine, Column, String, DateTime, Integer
    from sqlalchemy.types import JSON
    from sqlalchemy.orm import declarative_base, sessionmaker
except Exception:  # noqa: F401
    create_engine = None  # type: ignore
    Column = None  # type: ignore
    String = None  # type: ignore
    DateTime = None  # type: ignore
    Integer = None  # type: ignore
    JSON = None  # type: ignore
    declarative_base = None  # type: ignore
    sessionmaker = None  # type: ignore


class InMemoryDatabase:
    def __init__(self):
        self.assessments: Dict[str, AssessmentResult] = {}
        self.leads: Dict[str, Lead] = {}
        self.in_progress_assessments: Dict[str, InProgressAssessment] = {}
    
    def save_assessment(self, assessment: AssessmentResult) -> AssessmentResult:
        self.assessments[assessment.id] = assessment
        return assessment
    
    def get_assessment(self, assessment_id: str) -> Optional[AssessmentResult]:
        return self.assessments.get(assessment_id)
    
    def get_all_assessments(self) -> List[AssessmentResult]:
        return list(self.assessments.values())
    
    def save_lead(self, lead: Lead) -> Lead:
        self.leads[lead.id] = lead
        return lead
    
    def get_lead(self, lead_id: str) -> Optional[Lead]:
        return self.leads.get(lead_id)
    
    def get_all_leads(self) -> List[Lead]:
        return list(self.leads.values())
    
    def save_in_progress_assessment(self, assessment: InProgressAssessment) -> InProgressAssessment:
        self.in_progress_assessments[assessment.id] = assessment
        return assessment
    
    def get_in_progress_assessment(self, assessment_id: str) -> Optional[InProgressAssessment]:
        return self.in_progress_assessments.get(assessment_id)


DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL and create_engine is not None:
    if DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)
    Base = declarative_base()
    engine = create_engine(DATABASE_URL, future=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)

    class AssessmentORM(Base):
        __tablename__ = "assessments"
        id = Column(String, primary_key=True, index=True)
        submission_date = Column(DateTime, nullable=False)
        data = Column(JSON, nullable=False)

    class LeadORM(Base):
        __tablename__ = "leads"
        id = Column(String, primary_key=True, index=True)
        company_name = Column(String, nullable=False)
        contact_name = Column(String, nullable=False)
        email = Column(String, nullable=False)
        phone = Column(String, nullable=True)
        company_size = Column(String, nullable=False)
        industry = Column(String, nullable=True)
        employee_range = Column(String, nullable=True)
        operating_states = Column(JSON, nullable=True)
        business_age = Column(String, nullable=True)
        consent = Column(String, nullable=False, default="false")
        status = Column(String, nullable=False, default="started")
        ip_hash = Column(String, nullable=True)
        user_agent = Column(String, nullable=True)
        submission_date = Column(DateTime, nullable=False)
        overall_score = Column(Integer, nullable=True)
        overall_risk_level = Column(String, nullable=True)
        high_risk_categories = Column(JSON, nullable=True)

    Base.metadata.create_all(bind=engine)

    class SQLDatabase:
        def save_assessment(self, assessment: AssessmentResult) -> AssessmentResult:
            with SessionLocal() as session:
                payload = assessment.model_dump(mode="json")
                obj = AssessmentORM(
                    id=assessment.id,
                    submission_date=assessment.submission_date if isinstance(assessment.submission_date, datetime) else datetime.fromisoformat(str(assessment.submission_date)),
                    data=payload,
                )
                session.merge(obj)
                session.commit()
                return assessment

        def get_assessment(self, assessment_id: str) -> Optional[AssessmentResult]:
            with SessionLocal() as session:
                obj = session.get(AssessmentORM, assessment_id)
                if not obj:
                    return None
                return AssessmentResult.model_validate(obj.data)

        def get_all_assessments(self) -> List[AssessmentResult]:
            with SessionLocal() as session:
                rows = session.query(AssessmentORM).all()
                return [AssessmentResult.model_validate(r.data) for r in rows]

        def save_lead(self, lead: Lead) -> Lead:
            with SessionLocal() as session:
                obj = LeadORM(
                    id=lead.id,
                    company_name=lead.company_name,
                    contact_name=lead.contact_name,
                    email=str(lead.email),
                    phone=lead.phone,
                    company_size=lead.company_size,
                    industry=lead.industry,
                    employee_range=lead.employee_range,
                    operating_states=lead.operating_states,
                    business_age=lead.business_age,
                    consent=str(lead.consent).lower(),
                    status=str(lead.status),
                    ip_hash=lead.ip_hash,
                    user_agent=lead.user_agent,
                    submission_date=lead.submission_date if isinstance(lead.submission_date, datetime) else datetime.fromisoformat(str(lead.submission_date)),
                    overall_score=lead.overall_score,
                    overall_risk_level=str(lead.overall_risk_level) if lead.overall_risk_level else None,
                    high_risk_categories=lead.high_risk_categories,
                )
                session.merge(obj)
                session.commit()
                return lead

        def get_lead(self, lead_id: str) -> Optional[Lead]:
            with SessionLocal() as session:
                obj = session.get(LeadORM, lead_id)
                if not obj:
                    return None
                data = {
                    "id": obj.id,
                    "company_name": obj.company_name,
                    "contact_name": obj.contact_name,
                    "email": obj.email,
                    "phone": obj.phone,
                    "company_size": obj.company_size,
                    "industry": obj.industry,
                    "employee_range": obj.employee_range,
                    "operating_states": obj.operating_states,
                    "business_age": obj.business_age,
                    "consent": obj.consent.lower() == "true" if obj.consent else False,
                    "status": obj.status,
                    "ip_hash": obj.ip_hash,
                    "user_agent": obj.user_agent,
                    "submission_date": obj.submission_date.isoformat(),
                    "overall_score": obj.overall_score,
                    "overall_risk_level": obj.overall_risk_level,
                    "high_risk_categories": obj.high_risk_categories,
                }
                return Lead.model_validate(data)

        def get_all_leads(self) -> List[Lead]:
            with SessionLocal() as session:
                rows = session.query(LeadORM).all()
                out: List[Lead] = []
                for obj in rows:
                    data = {
                        "id": obj.id,
                        "company_name": obj.company_name,
                        "contact_name": obj.contact_name,
                        "email": obj.email,
                        "phone": obj.phone,
                        "company_size": obj.company_size,
                        "industry": obj.industry,
                        "employee_range": obj.employee_range,
                        "operating_states": obj.operating_states,
                        "business_age": obj.business_age,
                        "consent": obj.consent.lower() == "true" if obj.consent else False,
                        "status": obj.status,
                        "ip_hash": obj.ip_hash,
                        "user_agent": obj.user_agent,
                        "submission_date": obj.submission_date.isoformat(),
                        "overall_score": obj.overall_score,
                        "overall_risk_level": obj.overall_risk_level,
                        "high_risk_categories": obj.high_risk_categories,
                    }
                    out.append(Lead.model_validate(data))
                return out

    db = SQLDatabase()
else:
    db = InMemoryDatabase()
