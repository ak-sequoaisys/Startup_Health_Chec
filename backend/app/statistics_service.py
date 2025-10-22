from typing import List, Dict, Tuple
from datetime import datetime, timedelta
from collections import Counter
from app.models import AssessmentResult, Lead, LeadStatus
from app.database import db


class StatisticsService:
    def get_weekly_statistics(self) -> Dict:
        """
        Calculate weekly statistics for the digest email.
        Returns total assessments, average score, and top 5 states.
        """
        assessments = db.get_all_assessments()
        leads = db.get_all_leads()
        
        one_week_ago = datetime.now() - timedelta(days=7)
        
        weekly_assessments = [
            a for a in assessments 
            if a.submission_date >= one_week_ago
        ]
        
        total_assessments = len(weekly_assessments)
        
        if total_assessments > 0:
            total_score = sum(a.overall_percentage for a in weekly_assessments)
            avg_score = total_score / total_assessments
        else:
            avg_score = 0.0
        
        state_counter = Counter()
        for lead in leads:
            if lead.operating_states and lead.submission_date >= one_week_ago:
                for state in lead.operating_states:
                    state_counter[state] += 1
        
        top_5_states = state_counter.most_common(5)
        
        return {
            "total_assessments": total_assessments,
            "avg_score": avg_score,
            "top_5_states": top_5_states,
            "period_start": one_week_ago,
            "period_end": datetime.now()
        }
    
    def get_all_time_statistics(self) -> Dict:
        """
        Calculate all-time statistics.
        """
        assessments = db.get_all_assessments()
        leads = db.get_all_leads()
        
        total_assessments = len(assessments)
        
        if total_assessments > 0:
            total_score = sum(a.overall_percentage for a in assessments)
            avg_score = total_score / total_assessments
        else:
            avg_score = 0.0
        
        state_counter = Counter()
        for lead in leads:
            if lead.operating_states:
                for state in lead.operating_states:
                    state_counter[state] += 1
        
        top_5_states = state_counter.most_common(5)
        
        return {
            "total_assessments": total_assessments,
            "avg_score": avg_score,
            "top_5_states": top_5_states
        }


statistics_service = StatisticsService()
