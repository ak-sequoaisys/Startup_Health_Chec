#!/bin/bash
set -e

PR_NUMBER=$1

if [ -z "$PR_NUMBER" ]; then
    echo "Error: PR number is required"
    echo "Usage: ./deploy-preview.sh <pr-number>"
    exit 1
fi

STACK_NAME="startup-health-check-pr-${PR_NUMBER}"
CLUSTER_NAME="startup-health-check-preview-cluster"
SERVICE_NAME="startup-health-check-pr-${PR_NUMBER}"
TASK_FAMILY="startup-health-check-pr-${PR_NUMBER}"
REGION="${AWS_REGION:-us-east-1}"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo "=========================================="
echo "Deploying Preview Environment"
echo "=========================================="
echo "PR Number: $PR_NUMBER"
echo "Stack Name: $STACK_NAME"
echo "Region: $REGION"
echo "Account ID: $ACCOUNT_ID"
echo "=========================================="

echo "Checking for preview cluster..."
if ! aws ecs describe-clusters --clusters $CLUSTER_NAME --region $REGION --query 'clusters[0].status' --output text 2>/dev/null | grep -q "ACTIVE"; then
    echo "Creating preview cluster: $CLUSTER_NAME"
    aws ecs create-cluster \
        --cluster-name $CLUSTER_NAME \
        --region $REGION \
        --settings name=containerInsights,value=enabled
else
    echo "Preview cluster already exists"
fi

SHARED_STACK_NAME="startup-health-check-preview-shared"
if ! aws cloudformation describe-stacks --stack-name $SHARED_STACK_NAME --region $REGION 2>/dev/null; then
    echo "Creating shared preview infrastructure..."
    aws cloudformation deploy \
        --template-file cloudformation-preview-shared.yml \
        --stack-name $SHARED_STACK_NAME \
        --parameter-overrides \
            Environment=preview \
            DatabasePassword="${DATABASE_PASSWORD:-preview-db-password-change-me}" \
        --capabilities CAPABILITY_IAM \
        --region $REGION
    
    echo "Waiting for shared infrastructure to be ready..."
    aws cloudformation wait stack-create-complete \
        --stack-name $SHARED_STACK_NAME \
        --region $REGION
fi

echo "Getting shared infrastructure details..."
VPC_ID=$(aws cloudformation describe-stacks --stack-name $SHARED_STACK_NAME --region $REGION --query "Stacks[0].Outputs[?OutputKey=='VPCId'].OutputValue" --output text)
PUBLIC_SUBNET_1=$(aws cloudformation describe-stacks --stack-name $SHARED_STACK_NAME --region $REGION --query "Stacks[0].Outputs[?OutputKey=='PublicSubnet1Id'].OutputValue" --output text)
PUBLIC_SUBNET_2=$(aws cloudformation describe-stacks --stack-name $SHARED_STACK_NAME --region $REGION --query "Stacks[0].Outputs[?OutputKey=='PublicSubnet2Id'].OutputValue" --output text)
ECS_SECURITY_GROUP=$(aws cloudformation describe-stacks --stack-name $SHARED_STACK_NAME --region $REGION --query "Stacks[0].Outputs[?OutputKey=='ECSSecurityGroupId'].OutputValue" --output text)
ALB_ARN=$(aws cloudformation describe-stacks --stack-name $SHARED_STACK_NAME --region $REGION --query "Stacks[0].Outputs[?OutputKey=='LoadBalancerArn'].OutputValue" --output text)
ALB_LISTENER_ARN=$(aws cloudformation describe-stacks --stack-name $SHARED_STACK_NAME --region $REGION --query "Stacks[0].Outputs[?OutputKey=='ALBListenerArn'].OutputValue" --output text)
DB_ENDPOINT=$(aws cloudformation describe-stacks --stack-name $SHARED_STACK_NAME --region $REGION --query "Stacks[0].Outputs[?OutputKey=='DatabaseEndpoint'].OutputValue" --output text)

echo "VPC ID: $VPC_ID"
echo "Subnets: $PUBLIC_SUBNET_1, $PUBLIC_SUBNET_2"
echo "Security Group: $ECS_SECURITY_GROUP"
echo "Database: $DB_ENDPOINT"

echo "Creating target groups for PR $PR_NUMBER..."

BACKEND_TG_NAME="pr-${PR_NUMBER}-backend-tg"
FRONTEND_TG_NAME="pr-${PR_NUMBER}-frontend-tg"

aws elbv2 delete-target-group --target-group-arn $(aws elbv2 describe-target-groups --names $BACKEND_TG_NAME --query 'TargetGroups[0].TargetGroupArn' --output text 2>/dev/null) 2>/dev/null || true
aws elbv2 delete-target-group --target-group-arn $(aws elbv2 describe-target-groups --names $FRONTEND_TG_NAME --query 'TargetGroups[0].TargetGroupArn' --output text 2>/dev/null) 2>/dev/null || true

BACKEND_TG_ARN=$(aws elbv2 create-target-group \
    --name $BACKEND_TG_NAME \
    --protocol HTTP \
    --port 8000 \
    --vpc-id $VPC_ID \
    --target-type ip \
    --health-check-enabled \
    --health-check-path /healthz \
    --health-check-interval-seconds 30 \
    --health-check-timeout-seconds 5 \
    --healthy-threshold-count 2 \
    --unhealthy-threshold-count 3 \
    --matcher HttpCode=200 \
    --region $REGION \
    --query 'TargetGroups[0].TargetGroupArn' \
    --output text)

echo "Backend target group created: $BACKEND_TG_ARN"

FRONTEND_TG_ARN=$(aws elbv2 create-target-group \
    --name $FRONTEND_TG_NAME \
    --protocol HTTP \
    --port 80 \
    --vpc-id $VPC_ID \
    --target-type ip \
    --health-check-enabled \
    --health-check-path / \
    --health-check-interval-seconds 30 \
    --health-check-timeout-seconds 5 \
    --healthy-threshold-count 2 \
    --unhealthy-threshold-count 3 \
    --region $REGION \
    --query 'TargetGroups[0].TargetGroupArn' \
    --output text)

echo "Frontend target group created: $FRONTEND_TG_ARN"

echo "Configuring ALB listener rules..."

BACKEND_PRIORITY=$((1000 + PR_NUMBER))
aws elbv2 create-rule \
    --listener-arn $ALB_LISTENER_ARN \
    --priority $BACKEND_PRIORITY \
    --conditions Field=host-header,Values=pr-${PR_NUMBER}-api.deploymirror.com \
    --actions Type=forward,TargetGroupArn=$BACKEND_TG_ARN \
    --region $REGION 2>/dev/null || \
    aws elbv2 modify-rule \
        --rule-arn $(aws elbv2 describe-rules --listener-arn $ALB_LISTENER_ARN --query "Rules[?Priority=='$BACKEND_PRIORITY'].RuleArn" --output text) \
        --actions Type=forward,TargetGroupArn=$BACKEND_TG_ARN \
        --region $REGION

FRONTEND_PRIORITY=$((2000 + PR_NUMBER))
aws elbv2 create-rule \
    --listener-arn $ALB_LISTENER_ARN \
    --priority $FRONTEND_PRIORITY \
    --conditions Field=host-header,Values=pr-${PR_NUMBER}.deploymirror.com \
    --actions Type=forward,TargetGroupArn=$FRONTEND_TG_ARN \
    --region $REGION 2>/dev/null || \
    aws elbv2 modify-rule \
        --rule-arn $(aws elbv2 describe-rules --listener-arn $ALB_LISTENER_ARN --query "Rules[?Priority=='$FRONTEND_PRIORITY'].RuleArn" --output text) \
        --actions Type=forward,TargetGroupArn=$FRONTEND_TG_ARN \
        --region $REGION

echo "Creating database URL secret..."
DATABASE_URL="postgresql://postgres:${DATABASE_PASSWORD:-preview-db-password-change-me}@${DB_ENDPOINT}:5432/startup_health_check"

aws secretsmanager create-secret \
    --name "startup-health-check-pr-${PR_NUMBER}/database-url" \
    --secret-string "$DATABASE_URL" \
    --region $REGION 2>/dev/null || \
    aws secretsmanager update-secret \
        --secret-id "startup-health-check-pr-${PR_NUMBER}/database-url" \
        --secret-string "$DATABASE_URL" \
        --region $REGION

echo "Registering ECS task definition..."
cat > /tmp/task-def-pr-${PR_NUMBER}.json <<EOF
{
  "family": "${TASK_FAMILY}",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::${ACCOUNT_ID}:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::${ACCOUNT_ID}:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/startup-health-check-backend-preview:pr-${PR_NUMBER}",
      "essential": true,
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "ENVIRONMENT",
          "value": "preview"
        },
        {
          "name": "LOG_LEVEL",
          "value": "INFO"
        }
      ],
      "secrets": [
        {
          "name": "DATABASE_URL",
          "valueFrom": "arn:aws:secretsmanager:${REGION}:${ACCOUNT_ID}:secret:startup-health-check-pr-${PR_NUMBER}/database-url"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/startup-health-check-preview",
          "awslogs-region": "${REGION}",
          "awslogs-stream-prefix": "pr-${PR_NUMBER}-backend"
        }
      }
    },
    {
      "name": "frontend",
      "image": "${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/startup-health-check-frontend-preview:pr-${PR_NUMBER}",
      "essential": true,
      "portMappings": [
        {
          "containerPort": 80,
          "protocol": "tcp"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/startup-health-check-preview",
          "awslogs-region": "${REGION}",
          "awslogs-stream-prefix": "pr-${PR_NUMBER}-frontend"
        }
      }
    }
  ]
}
EOF

aws ecs register-task-definition \
    --cli-input-json file:///tmp/task-def-pr-${PR_NUMBER}.json \
    --region $REGION

echo "Creating/updating ECS service..."
if aws ecs describe-services \
    --cluster $CLUSTER_NAME \
    --services $SERVICE_NAME \
    --region $REGION \
    --query 'services[0].status' \
    --output text 2>/dev/null | grep -q "ACTIVE"; then
    
    echo "Updating existing service..."
    aws ecs update-service \
        --cluster $CLUSTER_NAME \
        --service $SERVICE_NAME \
        --task-definition $TASK_FAMILY \
        --force-new-deployment \
        --region $REGION
else
    echo "Creating new service..."
    aws ecs create-service \
        --cluster $CLUSTER_NAME \
        --service-name $SERVICE_NAME \
        --task-definition $TASK_FAMILY \
        --desired-count 1 \
        --launch-type FARGATE \
        --network-configuration "awsvpcConfiguration={subnets=[$PUBLIC_SUBNET_1,$PUBLIC_SUBNET_2],securityGroups=[$ECS_SECURITY_GROUP],assignPublicIp=ENABLED}" \
        --load-balancers "targetGroupArn=$BACKEND_TG_ARN,containerName=backend,containerPort=8000" "targetGroupArn=$FRONTEND_TG_ARN,containerName=frontend,containerPort=80" \
        --region $REGION
fi

echo ""
echo "=========================================="
echo "Preview Deployment Complete!"
echo "=========================================="
echo "Frontend URL: http://pr-${PR_NUMBER}.deploymirror.com"
echo "Backend API: http://pr-${PR_NUMBER}-api.deploymirror.com"
echo "Health Check: http://pr-${PR_NUMBER}-api.deploymirror.com/healthz"
echo "=========================================="
echo ""
echo "Note: DNS records need to be configured to point to the ALB"
echo "The service may take a few minutes to become healthy"
