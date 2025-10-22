# Deployment Guide

This guide covers deploying the Startup Compliance Health Check Tool to AWS using ECS Fargate.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Prerequisites](#prerequisites)
- [AWS Infrastructure Setup](#aws-infrastructure-setup)
- [Deployment Process](#deployment-process)
- [Monitoring and Logging](#monitoring-and-logging)
- [Email Configuration (SES)](#email-configuration-ses)
- [SSL/TLS Setup](#ssltls-setup)
- [Uptime Monitoring](#uptime-monitoring)
- [Troubleshooting](#troubleshooting)

## Architecture Overview

The application is deployed on AWS using the following services:

- **ECS Fargate**: Container orchestration for backend and frontend
- **Application Load Balancer (ALB)**: Traffic distribution and SSL termination
- **RDS PostgreSQL**: Managed database service
- **CloudWatch**: Logging and monitoring
- **AWS SES**: Email notifications with DKIM/SPF
- **Secrets Manager**: Secure credential storage
- **ECR**: Container image registry

### Architecture Diagram

```
Internet
    ↓
Application Load Balancer (ALB)
    ↓
    ├─→ Frontend (ECS Fargate) - Port 80
    └─→ Backend (ECS Fargate) - Port 8000
            ↓
        RDS PostgreSQL
            ↓
        AWS SES (Email)
```

## Prerequisites

Before deploying, ensure you have:

1. **AWS Account** with appropriate permissions
2. **AWS CLI** installed and configured
3. **Docker** installed locally
4. **Domain name** (optional but recommended)
5. **AWS SES** verified domain or email addresses

### Required IAM Permissions

Your AWS user/role needs permissions for:
- ECS (create clusters, services, tasks)
- ECR (create repositories, push images)
- RDS (create databases)
- CloudFormation (create/update stacks)
- Secrets Manager (create/update secrets)
- CloudWatch (create log groups, alarms, dashboards)
- IAM (create roles and policies)
- EC2 (VPC, subnets, security groups)
- Elastic Load Balancing (create ALBs, target groups)

## AWS Infrastructure Setup

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd Startup_Health_Chec
```

### Step 2: Set Environment Variables

Create a `.env.deploy` file with your configuration:

```bash
# Required
export STACK_NAME="startup-health-check"
export AWS_REGION="us-east-1"
export DATABASE_PASSWORD="your-secure-password"
export NOTIFICATION_EMAIL="service@offrd.co"
export SENDER_EMAIL="noreply@offrd.co"

# Optional - for SES email sending
export AWS_SES_ACCESS_KEY_ID="your-ses-access-key"
export AWS_SES_SECRET_ACCESS_KEY="your-ses-secret-key"

# Optional - for monitoring alerts
export ALARM_EMAIL="alerts@yourdomain.com"
```

Load the environment variables:

```bash
source .env.deploy
```

### Step 3: Deploy Infrastructure

Run the deployment script:

```bash
cd aws
./deploy.sh
```

This script will:
1. Create ECR repositories
2. Build and push Docker images
3. Deploy CloudFormation stack (VPC, RDS, ECS, ALB)
4. Create secrets in Secrets Manager
5. Register ECS task definition
6. Create/update ECS service

The deployment takes approximately 15-20 minutes.

### Step 4: Set Up Monitoring

After the infrastructure is deployed, set up CloudWatch monitoring:

```bash
./setup-monitoring.sh
```

This creates:
- CloudWatch dashboard
- SNS topic for alarms
- CloudWatch alarms for:
  - High error rate (5XX responses)
  - Unhealthy targets
  - High response time
  - High CPU/memory utilization
  - Database issues

## Deployment Process

### Initial Deployment

1. **Prepare environment variables** (see Step 2 above)
2. **Run deployment script**: `./deploy.sh`
3. **Wait for deployment** to complete
4. **Verify deployment**:
   ```bash
   # Get the load balancer DNS
   aws cloudformation describe-stacks \
     --stack-name $STACK_NAME \
     --query "Stacks[0].Outputs[?OutputKey=='LoadBalancerDNS'].OutputValue" \
     --output text
   ```
5. **Test the application**:
   ```bash
   curl http://<load-balancer-dns>/healthz
   ```

### Updating the Application

To deploy updates:

1. **Make code changes** and commit to git
2. **Rebuild and push images**:
   ```bash
   cd backend
   docker build -f Dockerfile.prod -t startup-health-check-backend:latest .
   docker tag startup-health-check-backend:latest $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/startup-health-check-backend:latest
   docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/startup-health-check-backend:latest
   ```
3. **Update ECS service**:
   ```bash
   aws ecs update-service \
     --cluster startup-health-check-cluster \
     --service startup-health-check-service \
     --force-new-deployment \
     --region $AWS_REGION
   ```

### Rolling Back

To rollback to a previous version:

```bash
# List task definition revisions
aws ecs list-task-definitions --family-prefix startup-health-check

# Update service to use previous revision
aws ecs update-service \
  --cluster startup-health-check-cluster \
  --service startup-health-check-service \
  --task-definition startup-health-check:PREVIOUS_REVISION \
  --region $AWS_REGION
```

## Monitoring and Logging

### CloudWatch Logs

Logs are stored in CloudWatch Logs at `/ecs/startup-health-check`.

**View logs**:
```bash
aws logs tail /ecs/startup-health-check --follow
```

**Query logs**:
```bash
aws logs filter-log-events \
  --log-group-name /ecs/startup-health-check \
  --filter-pattern "ERROR"
```

### CloudWatch Dashboard

Access the dashboard at:
```
https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=StartupHealthCheck
```

The dashboard shows:
- Response times (average and p99)
- Request count
- HTTP response codes (2XX, 4XX, 5XX)
- Target health
- ECS resource utilization
- RDS metrics
- Recent errors
- Email notification failures

### CloudWatch Alarms

Alarms are configured for:

| Alarm | Threshold | Description |
|-------|-----------|-------------|
| High Error Rate | >10 5XX errors in 5 min | Backend errors |
| Unhealthy Targets | ≥1 unhealthy target | Service health issues |
| High Response Time | >2 seconds average | Performance degradation |
| High CPU (ECS) | >80% for 10 min | Resource constraint |
| High Memory (ECS) | >80% for 10 min | Memory pressure |
| High DB CPU | >80% for 10 min | Database overload |
| Low DB Storage | <2GB free | Storage running out |

### Structured Logging

The application uses JSON-formatted structured logging for easy parsing and analysis.

**Log format**:
```json
{
  "timestamp": "2025-01-15T10:30:45.123Z",
  "level": "INFO",
  "logger": "app.main",
  "message": "Assessment completed",
  "service": "startup-compliance-health-check",
  "environment": "production",
  "assessment_id": "abc123",
  "score": 72.5,
  "risk_level": "MEDIUM"
}
```

**Environment variables for logging**:
- `LOG_LEVEL`: DEBUG, INFO, WARNING, ERROR, CRITICAL (default: INFO)
- `LOG_FORMAT`: json or text (default: json)
- `ENVIRONMENT`: development, staging, production

## Email Configuration (SES)

### Prerequisites

1. **Verify domain or email addresses** in AWS SES
2. **Request production access** (to send to any email)
3. **Configure DKIM and SPF** records

### SES Setup Steps

#### 1. Verify Domain

```bash
aws ses verify-domain-identity --domain offrd.co --region us-east-1
```

Add the verification TXT record to your DNS.

#### 2. Enable DKIM

```bash
aws ses verify-domain-dkim --domain offrd.co --region us-east-1
```

Add the three CNAME records to your DNS.

#### 3. Configure SPF

Add this TXT record to your DNS:
```
v=spf1 include:amazonses.com ~all
```

#### 4. Request Production Access

1. Go to AWS SES Console
2. Navigate to "Account dashboard"
3. Click "Request production access"
4. Fill out the form explaining your use case

#### 5. Configure Sending Authorization

If using IAM credentials for SES:

```bash
# Create IAM user for SES
aws iam create-user --user-name ses-sender

# Attach SES sending policy
aws iam attach-user-policy \
  --user-name ses-sender \
  --policy-arn arn:aws:iam::aws:policy/AmazonSESFullAccess

# Create access keys
aws iam create-access-key --user-name ses-sender
```

Store the access keys in Secrets Manager (done automatically by deploy script).

### Testing Email

Test email sending:

```bash
curl -X POST https://your-domain.com/api/v1/assessments/compute \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Test Company",
    "contact_name": "John Doe",
    "email": "john@test.com",
    "company_size": "10-50",
    "answers": [...]
  }'
```

Check CloudWatch Logs for email sending status.

## SSL/TLS Setup

### Option 1: AWS Certificate Manager (Recommended)

1. **Request certificate**:
   ```bash
   aws acm request-certificate \
     --domain-name yourdomain.com \
     --subject-alternative-names www.yourdomain.com api.yourdomain.com \
     --validation-method DNS \
     --region us-east-1
   ```

2. **Validate certificate**:
   - Add the CNAME records to your DNS
   - Wait for validation (usually 5-30 minutes)

3. **Update ALB listener**:
   ```bash
   # Get certificate ARN
   CERT_ARN=$(aws acm list-certificates --query "CertificateSummaryList[?DomainName=='yourdomain.com'].CertificateArn" --output text)
   
   # Get ALB ARN
   ALB_ARN=$(aws cloudformation describe-stacks \
     --stack-name $STACK_NAME \
     --query "Stacks[0].Resources[?LogicalResourceId=='ApplicationLoadBalancer'].PhysicalResourceId" \
     --output text)
   
   # Create HTTPS listener
   aws elbv2 create-listener \
     --load-balancer-arn $ALB_ARN \
     --protocol HTTPS \
     --port 443 \
     --certificates CertificateArn=$CERT_ARN \
     --default-actions Type=forward,TargetGroupArn=$FRONTEND_TARGET_GROUP
   ```

4. **Update DNS**:
   ```
   A record: yourdomain.com → ALB DNS (use alias)
   CNAME: www.yourdomain.com → yourdomain.com
   CNAME: api.yourdomain.com → yourdomain.com
   ```

### Option 2: Let's Encrypt

For Let's Encrypt, you'll need to:
1. Set up a reverse proxy (nginx) in front of the ALB
2. Use certbot to obtain certificates
3. Configure automatic renewal

## Uptime Monitoring

### Pingdom Setup

1. **Create Pingdom account** at https://www.pingdom.com
2. **Add uptime check**:
   - URL: `https://yourdomain.com/healthz`
   - Check interval: 1 minute
   - Alert contacts: Your email/SMS

3. **Configure alerts**:
   - Down for 2 minutes → Send alert
   - Response time > 3 seconds → Send warning

### Alternative: AWS Route 53 Health Checks

```bash
aws route53 create-health-check \
  --type HTTPS \
  --resource-path /healthz \
  --fully-qualified-domain-name yourdomain.com \
  --port 443 \
  --request-interval 30 \
  --failure-threshold 3
```

## Troubleshooting

### Application Not Starting

**Check ECS task logs**:
```bash
aws logs tail /ecs/startup-health-check --follow
```

**Common issues**:
- Database connection failure: Check DATABASE_URL secret
- Missing environment variables: Verify Secrets Manager
- Image pull errors: Check ECR permissions

### High Error Rate

**Check application logs**:
```bash
aws logs filter-log-events \
  --log-group-name /ecs/startup-health-check \
  --filter-pattern "ERROR" \
  --start-time $(date -u -d '1 hour ago' +%s)000
```

**Common causes**:
- Database connection pool exhausted
- Email service failures
- Invalid input data

### Database Connection Issues

**Check RDS status**:
```bash
aws rds describe-db-instances \
  --db-instance-identifier startup-health-check-postgres
```

**Test connection from ECS task**:
```bash
# Get task ID
TASK_ID=$(aws ecs list-tasks --cluster startup-health-check-cluster --query 'taskArns[0]' --output text)

# Execute command in task
aws ecs execute-command \
  --cluster startup-health-check-cluster \
  --task $TASK_ID \
  --container backend \
  --interactive \
  --command "/bin/bash"
```

### Email Not Sending

**Check SES sending statistics**:
```bash
aws ses get-send-statistics --region us-east-1
```

**Check audit logs**:
```bash
curl https://yourdomain.com/api/v1/audit-logs
```

**Common issues**:
- Email not verified in SES (sandbox mode)
- SES credentials incorrect
- SES sending limits reached
- Bounce/complaint rate too high

### Performance Issues

**Check CloudWatch metrics**:
- CPU utilization > 80%: Scale up ECS tasks
- Memory utilization > 80%: Increase task memory
- Database CPU > 80%: Upgrade RDS instance
- Response time > 2s: Check database queries

**Scale ECS service**:
```bash
aws ecs update-service \
  --cluster startup-health-check-cluster \
  --service startup-health-check-service \
  --desired-count 4 \
  --region $AWS_REGION
```

## Cost Optimization

### Estimated Monthly Costs (us-east-1)

| Service | Configuration | Estimated Cost |
|---------|--------------|----------------|
| ECS Fargate | 2 tasks (0.5 vCPU, 1GB) | ~$30 |
| RDS PostgreSQL | db.t3.micro | ~$15 |
| ALB | Standard | ~$20 |
| Data Transfer | 100GB | ~$9 |
| CloudWatch Logs | 10GB | ~$5 |
| **Total** | | **~$79/month** |

### Cost Reduction Tips

1. **Use Reserved Instances** for predictable workloads
2. **Enable auto-scaling** to scale down during low traffic
3. **Use S3 for log archival** after 30 days
4. **Optimize container images** to reduce storage costs
5. **Use CloudWatch Logs Insights** instead of exporting logs

## Security Best Practices

1. **Rotate credentials** regularly (every 90 days)
2. **Enable AWS GuardDuty** for threat detection
3. **Use AWS WAF** on ALB for DDoS protection
4. **Enable VPC Flow Logs** for network monitoring
5. **Implement least privilege** IAM policies
6. **Enable MFA** for AWS console access
7. **Regular security audits** using AWS Security Hub
8. **Keep dependencies updated** (run `poetry update`, `npm update`)

## Backup and Disaster Recovery

### Database Backups

RDS automatically creates daily backups with 7-day retention.

**Manual backup**:
```bash
aws rds create-db-snapshot \
  --db-instance-identifier startup-health-check-postgres \
  --db-snapshot-identifier manual-backup-$(date +%Y%m%d)
```

**Restore from backup**:
```bash
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier startup-health-check-postgres-restored \
  --db-snapshot-identifier manual-backup-20250115
```

### Disaster Recovery Plan

1. **RTO (Recovery Time Objective)**: 1 hour
2. **RPO (Recovery Point Objective)**: 24 hours (daily backups)

**Recovery steps**:
1. Restore RDS from latest snapshot
2. Update DATABASE_URL in Secrets Manager
3. Restart ECS service
4. Verify application health

## Support and Maintenance

### Regular Maintenance Tasks

**Weekly**:
- Review CloudWatch alarms
- Check error logs
- Monitor costs

**Monthly**:
- Update dependencies
- Review security patches
- Analyze performance metrics
- Review and optimize costs

**Quarterly**:
- Rotate credentials
- Security audit
- Disaster recovery drill
- Capacity planning review

### Getting Help

- **AWS Support**: https://console.aws.amazon.com/support/
- **CloudWatch Logs**: `/ecs/startup-health-check`
- **Application Logs**: Check structured JSON logs
- **Health Check**: `https://yourdomain.com/healthz`

## Additional Resources

- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [AWS RDS Documentation](https://docs.aws.amazon.com/rds/)
- [AWS SES Documentation](https://docs.aws.amazon.com/ses/)
- [CloudWatch Documentation](https://docs.aws.amazon.com/cloudwatch/)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
