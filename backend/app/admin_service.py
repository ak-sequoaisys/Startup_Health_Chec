from typing import List, Optional
from datetime import datetime
import csv
import io
from app.models import Lead, AssessmentResult
from app.admin_models import TrialRecord, TrialFilters
from app.database import db


def get_trials(filters: Optional[TrialFilters] = None) -> List[TrialRecord]:
    leads = db.get_all_leads()
    assessments = {a.id: a for a in db.get_all_assessments()}
    
    trials = []
    for lead in leads:
        assessment = assessments.get(lead.id)
        
        completed = None
        if assessment:
            completed = assessment.submission_date
        
        trial = TrialRecord(
            email=lead.email,
            company=lead.company_name,
            states=lead.operating_states,
            score=lead.overall_score,
            rating=lead.overall_risk_level,
            started=lead.submission_date,
            completed=completed,
            status=lead.status
        )
        
        if filters:
            if filters.start_date and trial.started < filters.start_date:
                continue
            if filters.end_date and trial.started > filters.end_date:
                continue
            if filters.states and trial.states:
                if not any(s in filters.states for s in trial.states):
                    continue
            if filters.score_min is not None and (trial.score is None or trial.score < filters.score_min):
                continue
            if filters.score_max is not None and (trial.score is None or trial.score > filters.score_max):
                continue
            if filters.status and trial.status != filters.status:
                continue
        
        trials.append(trial)
    
    trials.sort(key=lambda x: x.started, reverse=True)
    return trials


def export_trials_csv(trials: List[TrialRecord]) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow([
        "Email",
        "Company",
        "States",
        "Score",
        "Rating",
        "Started",
        "Completed",
        "Status"
    ])
    
    for trial in trials:
        writer.writerow([
            trial.email,
            trial.company,
            ",".join(trial.states) if trial.states else "",
            trial.score if trial.score is not None else "",
            trial.rating.value if trial.rating else "",
            trial.started.isoformat(),
            trial.completed.isoformat() if trial.completed else "",
            trial.status.value
        ])
    
    return output.getvalue()
