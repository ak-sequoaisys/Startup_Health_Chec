import os
import time
import uuid
from datetime import datetime
from typing import Optional
import boto3
from botocore.exceptions import ClientError
from app.models import AssessmentResult, AuditLog, EmailStatus
from app.database import db


class EmailService:
    def __init__(self):
        self.ses_client = None
        self.smtp_config = None
        self.recipient_email = os.getenv("NOTIFICATION_EMAIL", "service@offrd.co")
        self.sender_email = os.getenv("SENDER_EMAIL", "noreply@offrd.co")
        self.aws_region = os.getenv("AWS_REGION", "us-east-1")
        self.max_retries = 3
        
        aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        
        if aws_access_key and aws_secret_key:
            self.ses_client = boto3.client(
                'ses',
                region_name=self.aws_region,
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key
            )
    
    def _format_email_subject(self, company_name: str, email: str, score: float) -> str:
        return f"New Compliance Check – {company_name} ({email}) – Score {score:.1f}%"
    
    def _format_email_body(self, assessment: AssessmentResult) -> str:
        body = f"""
New Compliance Health Check Completed

Company Details:
- Company Name: {assessment.company_name}
- Contact Name: {assessment.contact_name}
- Email: {assessment.email}
- Company Size: {assessment.company_size if hasattr(assessment, 'company_size') else 'N/A'}
- Industry: {assessment.industry if hasattr(assessment, 'industry') else 'N/A'}

Assessment Results:
- Overall Score: {assessment.overall_percentage:.1f}%
- Risk Level: {assessment.overall_risk_level.value.upper()}
- Submission Date: {assessment.submission_date.strftime('%Y-%m-%d %H:%M:%S')}

Category Breakdown:
"""
        for cat_score in assessment.category_scores:
            body += f"\n{cat_score.category.value}:\n"
            body += f"  - Score: {cat_score.percentage:.1f}%\n"
            body += f"  - Risk Level: {cat_score.risk_level.value.upper()}\n"
            if cat_score.issues:
                body += f"  - Issues: {len(cat_score.issues)}\n"
        
        body += "\n\nPriority Actions:\n"
        for i, action in enumerate(assessment.priority_actions, 1):
            body += f"{i}. {action}\n"
        
        body += f"\n\nAssessment ID: {assessment.id}\n"
        
        return body
    
    def _send_via_ses(self, subject: str, body: str) -> tuple[bool, Optional[str]]:
        if not self.ses_client:
            return False, "SES client not configured"
        
        try:
            response = self.ses_client.send_email(
                Source=self.sender_email,
                Destination={
                    'ToAddresses': [self.recipient_email]
                },
                Message={
                    'Subject': {
                        'Data': subject,
                        'Charset': 'UTF-8'
                    },
                    'Body': {
                        'Text': {
                            'Data': body,
                            'Charset': 'UTF-8'
                        }
                    }
                }
            )
            return True, None
        except ClientError as e:
            error_message = e.response['Error']['Message']
            return False, f"SES Error: {error_message}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"
    
    def send_notification(self, assessment: AssessmentResult) -> AuditLog:
        subject = self._format_email_subject(
            assessment.company_name,
            str(assessment.email),
            assessment.overall_percentage
        )
        body = self._format_email_body(assessment)
        
        audit_log = AuditLog(
            id=str(uuid.uuid4()),
            assessment_id=assessment.id,
            company_name=assessment.company_name,
            email=assessment.email,
            score=assessment.overall_percentage,
            email_status=EmailStatus.PENDING,
            attempts=0,
            error_message=None,
            timestamp=datetime.now()
        )
        
        success = False
        last_error = None
        
        for attempt in range(1, self.max_retries + 1):
            audit_log.attempts = attempt
            
            success, error = self._send_via_ses(subject, body)
            
            if success:
                audit_log.email_status = EmailStatus.SUCCESS
                break
            else:
                last_error = error
                if attempt < self.max_retries:
                    time.sleep(2 ** attempt)
        
        if not success:
            audit_log.email_status = EmailStatus.FAILED
            audit_log.error_message = last_error
        
        db.save_audit_log(audit_log)
        
        return audit_log


email_service = EmailService()
