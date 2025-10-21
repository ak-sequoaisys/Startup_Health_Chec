#!/bin/bash
set -e

STACK_NAME="${STACK_NAME:-startup-health-check}"
REGION="${AWS_REGION:-us-east-1}"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo "Deploying Startup Health Check to AWS"
echo "Stack Name: $STACK_NAME"
echo "Region: $REGION"
echo "Account ID: $ACCOUNT_ID"

if [ -z "$DATABASE_PASSWORD" ]; then
    echo "Error: DATABASE_PASSWORD environment variable is required"
    exit 1
fi

if [ -z "$NOTIFICATION_EMAIL" ]; then
    echo "Error: NOTIFICATION_EMAIL environment variable is required"
    exit 1
fi

if [ -z "$SENDER_EMAIL" ]; then
    echo "Error: SENDER_EMAIL environment variable is required"
    exit 1
fi

echo "Creating ECR repositories..."
aws ecr describe-repositories --repository-names startup-health-check-backend --region $REGION 2>/dev/null || \
    aws ecr create-repository --repository-name startup-health-check-backend --region $REGION

aws ecr describe-repositories --repository-names startup-health-check-frontend --region $REGION 2>/dev/null || \
    aws ecr create-repository --repository-name startup-health-check-frontend --region $REGION

echo "Logging into ECR..."
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

echo "Building and pushing backend image..."
cd ../backend
docker build -f Dockerfile.prod -t startup-health-check-backend:latest .
docker tag startup-health-check-backend:latest $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/startup-health-check-backend:latest
docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/startup-health-check-backend:latest

echo "Building and pushing frontend image..."
cd ../frontend
docker build -f Dockerfile.prod --build-arg VITE_API_URL=https://api.yourdomain.com -t startup-health-check-frontend:latest .
docker tag startup-health-check-frontend:latest $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/startup-health-check-frontend:latest
docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/startup-health-check-frontend:latest

cd ../aws

echo "Deploying CloudFormation stack..."
aws cloudformation deploy \
    --template-file cloudformation-template.yml \
    --stack-name $STACK_NAME \
    --parameter-overrides \
        Environment=production \
        DatabasePassword=$DATABASE_PASSWORD \
        NotificationEmail=$NOTIFICATION_EMAIL \
        SenderEmail=$SENDER_EMAIL \
    --capabilities CAPABILITY_IAM \
    --region $REGION

echo "Getting stack outputs..."
ALB_DNS=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION --query "Stacks[0].Outputs[?OutputKey=='LoadBalancerDNS'].OutputValue" --output text)
DB_ENDPOINT=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION --query "Stacks[0].Outputs[?OutputKey=='DatabaseEndpoint'].OutputValue" --output text)
CLUSTER_NAME=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION --query "Stacks[0].Outputs[?OutputKey=='ECSClusterName'].OutputValue" --output text)

echo "Creating secrets in Secrets Manager..."
DATABASE_URL="postgresql://postgres:${DATABASE_PASSWORD}@${DB_ENDPOINT}:5432/startup_health_check"

aws secretsmanager create-secret \
    --name startup-health-check/database-url \
    --secret-string "$DATABASE_URL" \
    --region $REGION 2>/dev/null || \
    aws secretsmanager update-secret \
        --secret-id startup-health-check/database-url \
        --secret-string "$DATABASE_URL" \
        --region $REGION

aws secretsmanager create-secret \
    --name startup-health-check/notification-email \
    --secret-string "$NOTIFICATION_EMAIL" \
    --region $REGION 2>/dev/null || \
    aws secretsmanager update-secret \
        --secret-id startup-health-check/notification-email \
        --secret-string "$NOTIFICATION_EMAIL" \
        --region $REGION

aws secretsmanager create-secret \
    --name startup-health-check/sender-email \
    --secret-string "$SENDER_EMAIL" \
    --region $REGION 2>/dev/null || \
    aws secretsmanager update-secret \
        --secret-id startup-health-check/sender-email \
        --secret-string "$SENDER_EMAIL" \
        --region $REGION

if [ ! -z "$AWS_SES_ACCESS_KEY_ID" ] && [ ! -z "$AWS_SES_SECRET_ACCESS_KEY" ]; then
    aws secretsmanager create-secret \
        --name startup-health-check/aws-access-key-id \
        --secret-string "$AWS_SES_ACCESS_KEY_ID" \
        --region $REGION 2>/dev/null || \
        aws secretsmanager update-secret \
            --secret-id startup-health-check/aws-access-key-id \
            --secret-string "$AWS_SES_ACCESS_KEY_ID" \
            --region $REGION

    aws secretsmanager create-secret \
        --name startup-health-check/aws-secret-access-key \
        --secret-string "$AWS_SES_SECRET_ACCESS_KEY" \
        --region $REGION 2>/dev/null || \
        aws secretsmanager update-secret \
            --secret-id startup-health-check/aws-secret-access-key \
            --secret-string "$AWS_SES_SECRET_ACCESS_KEY" \
            --region $REGION
fi

echo "Updating ECS task definition..."
sed -e "s/ACCOUNT_ID/$ACCOUNT_ID/g" \
    -e "s/REGION/$REGION/g" \
    ecs-task-definition.json > ecs-task-definition-updated.json

aws ecs register-task-definition \
    --cli-input-json file://ecs-task-definition-updated.json \
    --region $REGION

echo "Creating ECS service..."
BACKEND_TARGET_GROUP=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION --query "Stacks[0].Outputs[?OutputKey=='BackendTargetGroupArn'].OutputValue" --output text)
FRONTEND_TARGET_GROUP=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION --query "Stacks[0].Outputs[?OutputKey=='FrontendTargetGroupArn'].OutputValue" --output text)
SECURITY_GROUP=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION --query "Stacks[0].Outputs[?OutputKey=='ECSSecurityGroupId'].OutputValue" --output text)
SUBNET1=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION --query "Stacks[0].Outputs[?OutputKey=='PublicSubnet1Id'].OutputValue" --output text)
SUBNET2=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION --query "Stacks[0].Outputs[?OutputKey=='PublicSubnet2Id'].OutputValue" --output text)

aws ecs create-service \
    --cluster $CLUSTER_NAME \
    --service-name startup-health-check-service \
    --task-definition startup-health-check \
    --desired-count 2 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[$SUBNET1,$SUBNET2],securityGroups=[$SECURITY_GROUP],assignPublicIp=ENABLED}" \
    --load-balancers "targetGroupArn=$BACKEND_TARGET_GROUP,containerName=backend,containerPort=8000" "targetGroupArn=$FRONTEND_TARGET_GROUP,containerName=frontend,containerPort=80" \
    --region $REGION 2>/dev/null || \
    aws ecs update-service \
        --cluster $CLUSTER_NAME \
        --service startup-health-check-service \
        --task-definition startup-health-check \
        --force-new-deployment \
        --region $REGION

echo ""
echo "Deployment complete!"
echo "Load Balancer DNS: $ALB_DNS"
echo "Database Endpoint: $DB_ENDPOINT"
echo ""
echo "Next steps:"
echo "1. Configure DNS to point to the load balancer"
echo "2. Set up SSL certificate in ACM and update ALB listener"
echo "3. Verify SES domain and configure DKIM/SPF"
echo "4. Set up CloudWatch dashboards and alarms"
echo "5. Configure Pingdom or similar for uptime monitoring"
