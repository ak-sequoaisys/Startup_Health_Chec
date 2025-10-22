from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from app.models import RiskLevel, LeadStatus


class TrialRecord(BaseModel):
    email: EmailStr
    company: str
    states: Optional[List[str]]
    score: Optional[float]
    rating: Optional[RiskLevel]
    started: datetime
    completed: Optional[datetime]
    status: LeadStatus


class TrialFilters(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    states: Optional[List[str]] = None
    score_min: Optional[float] = None
    score_max: Optional[float] = None
    status: Optional[LeadStatus] = None
