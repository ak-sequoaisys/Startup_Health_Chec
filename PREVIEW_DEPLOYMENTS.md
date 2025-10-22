# Preview Deployments Guide

This document explains how the automated preview deployment system works for pull requests.

## Overview

Every pull request automatically gets its own isolated preview environment deployed to AWS. This allows you to test changes before merging to production.

## How It Works

### Automatic Deployment

When you create or update a pull request:

1. **GitHub Actions triggers** the preview deployment workflow
2. **Docker images are built** for both backend and frontend
3. **Images are pushed** to Amazon ECR (Elastic Container Registry)
4. **ECS service is created/updated** with the new images
5. **Target groups and ALB rules** are configured for routing
6. **Deployment URL is posted** as a comment on the PR

### Preview Environment URLs

Each PR gets unique URLs:

- **Frontend**: `http://pr-{number}.deploymirror.com`
- **Backend API**: `http://pr-{number}-api.deploymirror.com`
- **Health Check**: `http://pr-{number}-api.deploymirror.com/healthz`

Example for PR #42:
- Frontend: `http://pr-42.deploymirror.com`
- Backend: `http://pr-42-api.deploymirror.com`

### Automatic Cleanup

When a PR is closed or merged:

1. **ECS service is deleted**
2. **Task definitions are deregistered**
3. **Target groups are removed**
4. **Docker images are deleted** from ECR
5. **Secrets are cleaned up**
6. **Cleanup confirmation** is posted as a comment

## Architecture

### Shared Infrastructure

All preview environments share common infrastructure to reduce costs:

- **VPC**: Single VPC for all previews (10.1.0.0/16)
- **RDS Database**: Shared PostgreSQL instance (db.t3.micro)
- **Application Load Balancer**: Single ALB with host-based routing
- **ECS Cluster**: `startup-health-check-preview-cluster`

### Per-PR Resources

Each PR gets its own:

- **ECS Service**: `startup-health-check-pr-{number}`
- **Task Definition**: `startup-health-check-pr-{number}`
- **Target Groups**: Backend and frontend target groups
- **ALB Listener Rules**: Host-based routing rules
- **Secrets**: Database connection string
- **Docker Images**: Tagged as `pr-{number}`

### Resource Naming Convention

| Resource Type | Naming Pattern |
|--------------|----------------|
| ECS Service | `startup-health-check-pr-{number}` |
| Task Definition | `startup-health-check-pr-{number}` |
| Backend Target Group | `pr-{number}-backend-tg` |
| Frontend Target Group | `pr-{number}-frontend-tg` |
| Docker Image Tag | `pr-{number}` |
| Secret | `startup-health-check-pr-{number}/database-url` |

## Setup Requirements

### AWS Configuration

#### 1. Create IAM Role for GitHub Actions

Create an IAM role with OIDC provider for GitHub Actions:

```bash
# Create OIDC provider (one-time setup)
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1

# Create trust policy
cat > trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:ak-sequoaisys/Startup_Health_Chec:*"
        }
      }
    }
  ]
}
EOF

# Create role
aws iam create-role \
  --role-name GitHubActionsDeployRole \
  --assume-role-policy-document file://trust-policy.json

# Attach policies
aws iam attach-role-policy \
  --role-name GitHubActionsDeployRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonECS_FullAccess

aws iam attach-role-policy \
  --role-name GitHubActionsDeployRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryPowerUser

aws iam attach-role-policy \
  --role-name GitHubActionsDeployRole \
  --policy-arn arn:aws:iam::aws:policy/CloudFormationFullAccess

aws iam attach-role-policy \
  --role-name GitHubActionsDeployRole \
  --policy-arn arn:aws:iam::aws:policy/SecretsManagerReadWrite
```

#### 2. Create ECS Task Execution and Task Roles

```bash
# Create task execution role
aws iam create-role \
  --role-name ecsTaskExecutionRole \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "ecs-tasks.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }]
  }'

aws iam attach-role-policy \
  --role-name ecsTaskExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy

# Create task role
aws iam create-role \
  --role-name ecsTaskRole \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "ecs-tasks.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }]
  }'

aws iam attach-role-policy \
  --role-name ecsTaskRole \
  --policy-arn arn:aws:iam::aws:policy/CloudWatchLogsFullAccess
```

#### 3. Configure GitHub Secrets

Add the following secrets to your GitHub repository:

| Secret Name | Description | Example Value |
|------------|-------------|---------------|
| `AWS_ROLE_ARN` | IAM role ARN for GitHub Actions | `arn:aws:iam::123456789012:role/GitHubActionsDeployRole` |
| `DATABASE_PASSWORD` | PostgreSQL password for preview DB | `secure-password-here` |

To add secrets:
1. Go to repository Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add each secret with its value

### DNS Configuration

Configure DNS records to point to the ALB:

```
# Get ALB DNS name
aws cloudformation describe-stacks \
  --stack-name startup-health-check-preview-shared \
  --query "Stacks[0].Outputs[?OutputKey=='LoadBalancerDNS'].OutputValue" \
  --output text

# Add wildcard DNS records
*.deploymirror.com CNAME <alb-dns-name>
```

Or configure individual records:
```
pr-*.deploymirror.com CNAME <alb-dns-name>
```

## Usage

### For Developers

#### Creating a Preview

1. **Create a pull request** against `devin/1760895937-compliance-health-check-tool` or `main`
2. **Wait for deployment** (typically 5-10 minutes)
3. **Check PR comments** for deployment URLs
4. **Test your changes** using the preview URLs

#### Updating a Preview

1. **Push new commits** to your PR branch
2. **Deployment automatically updates** with new changes
3. **Check PR comments** for updated deployment status

#### Testing the Preview

```bash
# Check backend health
curl http://pr-{number}-api.deploymirror.com/healthz

# Test API endpoint
curl http://pr-{number}-api.deploymirror.com/api/v1/questions

# Visit frontend
open http://pr-{number}.deploymirror.com
```

### For Reviewers

1. **Click the preview URL** in the PR comment
2. **Test the full application flow**:
   - Fill out the contact form
   - Complete the assessment
   - Review the results page
3. **Check the backend API** health endpoint
4. **Leave feedback** on the PR

## Monitoring

### CloudWatch Logs

View logs for a specific PR:

```bash
# Backend logs
aws logs tail /ecs/startup-health-check-preview \
  --follow \
  --filter-pattern "pr-{number}-backend"

# Frontend logs
aws logs tail /ecs/startup-health-check-preview \
  --follow \
  --filter-pattern "pr-{number}-frontend"
```

### ECS Service Status

Check service health:

```bash
aws ecs describe-services \
  --cluster startup-health-check-preview-cluster \
  --services startup-health-check-pr-{number} \
  --query 'services[0].{Status:status,Running:runningCount,Desired:desiredCount}'
```

### Task Status

View running tasks:

```bash
aws ecs list-tasks \
  --cluster startup-health-check-preview-cluster \
  --service-name startup-health-check-pr-{number}
```

## Troubleshooting

### Deployment Failed

**Check GitHub Actions logs**:
1. Go to the PR
2. Click "Checks" tab
3. Click on the failed workflow
4. Review the logs

**Common issues**:
- AWS credentials not configured
- ECR repository doesn't exist
- Task definition registration failed
- Service creation failed

### Preview Not Accessible

**Check ALB target health**:
```bash
aws elbv2 describe-target-health \
  --target-group-arn $(aws elbv2 describe-target-groups \
    --names pr-{number}-backend-tg \
    --query 'TargetGroups[0].TargetGroupArn' \
    --output text)
```

**Common issues**:
- DNS not configured
- Target group unhealthy
- Security group blocking traffic
- Container failing health checks

### Database Connection Issues

**Check database endpoint**:
```bash
aws cloudformation describe-stacks \
  --stack-name startup-health-check-preview-shared \
  --query "Stacks[0].Outputs[?OutputKey=='DatabaseEndpoint'].OutputValue" \
  --output text
```

**Check secret**:
```bash
aws secretsmanager get-secret-value \
  --secret-id startup-health-check-pr-{number}/database-url \
  --query SecretString \
  --output text
```

### Cleanup Not Working

**Manually delete resources**:
```bash
# Delete service
aws ecs delete-service \
  --cluster startup-health-check-preview-cluster \
  --service startup-health-check-pr-{number} \
  --force

# Delete target groups
aws elbv2 delete-target-group \
  --target-group-arn $(aws elbv2 describe-target-groups \
    --names pr-{number}-backend-tg \
    --query 'TargetGroups[0].TargetGroupArn' \
    --output text)

# Delete images
aws ecr batch-delete-image \
  --repository-name startup-health-check-backend-preview \
  --image-ids imageTag=pr-{number}
```

## Cost Optimization

### Estimated Costs Per Preview

| Resource | Configuration | Monthly Cost (if running 24/7) |
|----------|--------------|-------------------------------|
| ECS Task | 0.5 vCPU, 1GB | ~$15 |
| Target Groups | 2 per PR | ~$0.50 |
| Data Transfer | Minimal | ~$1 |
| **Total per PR** | | **~$16.50/month** |

### Shared Infrastructure Costs

| Resource | Configuration | Monthly Cost |
|----------|--------------|--------------|
| RDS PostgreSQL | db.t3.micro | ~$15 |
| Application Load Balancer | Standard | ~$20 |
| VPC | Standard | Free |
| CloudWatch Logs | 5GB | ~$2.50 |
| **Total shared** | | **~$37.50/month** |

### Cost Reduction Tips

1. **Close PRs promptly** - Resources are cleaned up automatically
2. **Limit concurrent PRs** - Each PR costs ~$16.50/month if left running
3. **Use preview environments for testing only** - Not for long-term staging
4. **Review open PRs weekly** - Close stale PRs to free resources

## Limitations

### Current Limitations

- **No SSL/TLS**: Preview environments use HTTP only
- **Shared database**: All previews share the same database (data isolation via app logic)
- **No custom domains**: Uses deploymirror.com subdomain pattern
- **Limited to 999 concurrent PRs**: Due to ALB listener rule priority limits
- **No email sending**: SES not configured for preview environments

### Future Enhancements

- [ ] SSL/TLS certificates via Let's Encrypt or ACM
- [ ] Per-PR database isolation
- [ ] Custom domain support
- [ ] Email testing with Mailhog or similar
- [ ] Performance testing integration
- [ ] Automated E2E tests on preview
- [ ] Cost tracking per PR
- [ ] Auto-shutdown after inactivity

## Security Considerations

### Data Isolation

- Preview environments share a database
- Use unique prefixes or schemas per PR if needed
- Don't use production data in previews

### Access Control

- Preview URLs are publicly accessible
- Consider adding basic auth for sensitive previews
- Don't commit secrets or credentials

### Secrets Management

- All secrets stored in AWS Secrets Manager
- Secrets are PR-specific and cleaned up automatically
- Never log or expose secrets in application code

## Support

### Getting Help

If you encounter issues:

1. **Check GitHub Actions logs** for deployment errors
2. **Review CloudWatch logs** for application errors
3. **Check this documentation** for troubleshooting steps
4. **Ask in the PR comments** for help from the team

### Reporting Issues

When reporting preview deployment issues, include:

- PR number
- Error message from GitHub Actions
- CloudWatch log excerpts
- Steps to reproduce
- Expected vs actual behavior
