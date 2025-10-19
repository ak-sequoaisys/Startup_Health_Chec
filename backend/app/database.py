from typing import Dict, List, Optional
from app.models import AssessmentResult, Lead


class InMemoryDatabase:
    def __init__(self):
        self.assessments: Dict[str, AssessmentResult] = {}
        self.leads: Dict[str, Lead] = {}
    
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


db = InMemoryDatabase()
