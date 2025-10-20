# Email Notification Setup Guide

This document explains how to configure and use the email notification feature for the Startup Compliance Health Check Tool.

## Overview

When a compliance assessment is completed, the system automatically sends an email notification to `service@offrd.co` with the following information:
- Company details (name, contact, email, size, industry)
- Overall compliance score and risk level
- Category-by-category breakdown
- Priority actions
- Assessment ID for reference

## Features

- **AWS SES Integration**: Uses Amazon Simple Email Service for reliable email delivery
- **Retry Logic**: Automatically retries failed emails up to 3 times with exponential backoff
- **Audit Logging**: All email attempts are logged with success/failure status
- **DKIM/SPF Support**: When properly configured with AWS SES, emails are sent with DKIM and SPF authentication

## Configuration

### Required Environment Variables

Add the following environment variables to your `.env` file:

```bash
# AWS SES Configuration
AWS_ACCESS_KEY_ID=your-aws-access-key-id
AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
AWS_REGION=us-east-1

# Email Notification Configuration
NOTIFICATION_EMAIL=service@offrd.co
SENDER_EMAIL=noreply@offrd.co
```

### AWS SES Setup

1. **Create an AWS Account** (if you don't have one)
   - Go to https://aws.amazon.com/
   - Sign up for an account

2. **Verify Email Addresses**
   - Go to AWS SES Console
   - Navigate to "Verified identities"
   - Verify both sender email (`noreply@offrd.co`) and recipient email (`service@offrd.co`)
   - For production, verify the entire domain instead of individual emails

3. **Request Production Access** (if needed)
   - By default, SES is in sandbox mode (can only send to verified emails)
   - Request production access to send to any email address
   - Go to "Account dashboard" → "Request production access"

4. **Configure DKIM and SPF**
   - In the verified identity settings, enable DKIM
   - Add the provided DKIM CNAME records to your DNS
   - Add SPF record to your DNS: `v=spf1 include:amazonses.com ~all`

5. **Create IAM User** (recommended for security)
   - Go to IAM Console
   - Create a new user with programmatic access
   - Attach the `AmazonSESFullAccess` policy (or create a custom policy with minimal permissions)
   - Save the Access Key ID and Secret Access Key

## Email Format

### Subject Line
```
New Compliance Check – {Company Name} ({Email}) – Score {Score}%
```

Example:
```
New Compliance Check – Acme Corp (john@acme.com) – Score 72.5%
```

### Email Body

The email includes:
- Company details (name, contact, email, size, industry)
- Overall score, risk level, and submission date
- Category breakdown with scores, risk levels, and issue counts
- Priority actions list
- Assessment ID for reference

## Retry Logic

The system implements a robust retry mechanism:

1. **Maximum Retries**: 3 attempts
2. **Exponential Backoff**: 
   - 1st retry: 2 seconds delay
   - 2nd retry: 4 seconds delay
   - 3rd retry: 8 seconds delay
3. **Error Handling**: Failures are logged but don't block the assessment completion

## Audit Logging

All email notifications are logged in the `audit_logs` table with:
- Assessment ID
- Company name and email
- Score
- Email status (SUCCESS, FAILED, PENDING)
- Number of attempts
- Error message (if failed)
- Timestamp

### API Endpoints for Audit Logs

```bash
# Get all audit logs
GET /api/v1/audit-logs

# Get specific audit log
GET /api/v1/audit-logs/{audit_log_id}
```

## Testing

### Local Testing (without AWS SES)

If AWS credentials are not configured, the email service will fail gracefully and log an error. The assessment will still complete successfully.

### Testing with AWS SES

1. Set up environment variables with valid AWS credentials
2. Ensure sender and recipient emails are verified in SES
3. Submit a test assessment through the API
4. Check the audit logs to verify email was sent successfully

```bash
# Submit a test assessment
curl -X POST http://localhost:8000/api/v1/assessments/compute \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Test Company",
    "contact_name": "John Doe",
    "email": "john@test.com",
    "company_size": "10-50",
    "answers": [...]
  }'

# Check audit logs
curl http://localhost:8000/api/v1/audit-logs
```

## Troubleshooting

### Email Not Sending

1. **Check AWS Credentials**: Ensure `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` are set correctly
2. **Verify Email Addresses**: In SES sandbox mode, both sender and recipient must be verified
3. **Check IAM Permissions**: Ensure the IAM user has SES send permissions
4. **Review Audit Logs**: Check `/api/v1/audit-logs` for error messages

### Common Errors

- **"Email address not verified"**: Verify the sender email in AWS SES console
- **"Access Denied"**: Check IAM permissions for the user
- **"Message rejected"**: Check SES sending limits and reputation
- **"Invalid credentials"**: Verify AWS access key and secret key

## Security Considerations

1. **Never commit AWS credentials** to version control
2. **Use IAM roles** when running on AWS infrastructure (EC2, ECS, Lambda)
3. **Rotate credentials** regularly
4. **Use minimal IAM permissions** (only SES send permission)
5. **Monitor SES usage** to detect unauthorized access

## Production Deployment

For production deployment:

1. Move SES out of sandbox mode
2. Verify the entire domain (not just individual emails)
3. Configure DKIM and SPF records
4. Set up CloudWatch alarms for SES metrics
5. Use IAM roles instead of access keys when possible
6. Configure bounce and complaint handling
7. Monitor email reputation and deliverability

## Cost

AWS SES pricing (as of 2024):
- First 62,000 emails per month: Free (when sent from EC2)
- After that: $0.10 per 1,000 emails
- Data transfer charges may apply

For most startups, the cost will be minimal or free.
