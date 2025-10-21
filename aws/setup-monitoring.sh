#!/bin/bash
set -e

STACK_NAME="${STACK_NAME:-startup-health-check}"
REGION="${AWS_REGION:-us-east-1}"
DASHBOARD_NAME="${DASHBOARD_NAME:-StartupHealthCheck}"

echo "Setting up monitoring for Startup Health Check"
echo "Stack Name: $STACK_NAME"
echo "Region: $REGION"
echo "Dashboard Name: $DASHBOARD_NAME"

LOAD_BALANCER=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query "Stacks[0].Outputs[?OutputKey=='LoadBalancerDNS'].OutputValue" \
    --output text | cut -d'-' -f1)

CLUSTER_NAME=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query "Stacks[0].Outputs[?OutputKey=='ECSClusterName'].OutputValue" \
    --output text)

DB_INSTANCE=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query "Stacks[0].Resources[?LogicalResourceId=='PostgresDB'].PhysicalResourceId" \
    --output text)

echo "Creating CloudWatch Dashboard..."
DASHBOARD_BODY=$(cat cloudwatch-dashboard.json | \
    sed "s/\"region\": \"us-east-1\"/\"region\": \"$REGION\"/g")

aws cloudwatch put-dashboard \
    --dashboard-name $DASHBOARD_NAME \
    --dashboard-body "$DASHBOARD_BODY" \
    --region $REGION

echo "Setting up SNS topic for alarms..."
SNS_TOPIC_ARN=$(aws sns create-topic \
    --name startup-health-check-alarms \
    --region $REGION \
    --query 'TopicArn' \
    --output text)

echo "SNS Topic ARN: $SNS_TOPIC_ARN"

if [ ! -z "$ALARM_EMAIL" ]; then
    echo "Subscribing $ALARM_EMAIL to SNS topic..."
    aws sns subscribe \
        --topic-arn $SNS_TOPIC_ARN \
        --protocol email \
        --notification-endpoint $ALARM_EMAIL \
        --region $REGION
    
    echo "Please check $ALARM_EMAIL and confirm the subscription"
fi

echo "Creating CloudWatch alarms..."

aws cloudwatch put-metric-alarm \
    --alarm-name "${STACK_NAME}-high-error-rate" \
    --alarm-description "Alert when 5XX error rate is high" \
    --metric-name HTTPCode_Target_5XX_Count \
    --namespace AWS/ApplicationELB \
    --statistic Sum \
    --period 300 \
    --evaluation-periods 2 \
    --threshold 10 \
    --comparison-operator GreaterThanThreshold \
    --alarm-actions $SNS_TOPIC_ARN \
    --region $REGION

aws cloudwatch put-metric-alarm \
    --alarm-name "${STACK_NAME}-unhealthy-targets" \
    --alarm-description "Alert when targets are unhealthy" \
    --metric-name UnHealthyHostCount \
    --namespace AWS/ApplicationELB \
    --statistic Average \
    --period 60 \
    --evaluation-periods 2 \
    --threshold 1 \
    --comparison-operator GreaterThanOrEqualToThreshold \
    --alarm-actions $SNS_TOPIC_ARN \
    --region $REGION

aws cloudwatch put-metric-alarm \
    --alarm-name "${STACK_NAME}-high-response-time" \
    --alarm-description "Alert when response time is high" \
    --metric-name TargetResponseTime \
    --namespace AWS/ApplicationELB \
    --statistic Average \
    --period 300 \
    --evaluation-periods 2 \
    --threshold 2.0 \
    --comparison-operator GreaterThanThreshold \
    --alarm-actions $SNS_TOPIC_ARN \
    --region $REGION

aws cloudwatch put-metric-alarm \
    --alarm-name "${STACK_NAME}-high-cpu-utilization" \
    --alarm-description "Alert when ECS CPU utilization is high" \
    --metric-name CPUUtilization \
    --namespace AWS/ECS \
    --statistic Average \
    --period 300 \
    --evaluation-periods 2 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --alarm-actions $SNS_TOPIC_ARN \
    --region $REGION

aws cloudwatch put-metric-alarm \
    --alarm-name "${STACK_NAME}-high-memory-utilization" \
    --alarm-description "Alert when ECS memory utilization is high" \
    --metric-name MemoryUtilization \
    --namespace AWS/ECS \
    --statistic Average \
    --period 300 \
    --evaluation-periods 2 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --alarm-actions $SNS_TOPIC_ARN \
    --region $REGION

aws cloudwatch put-metric-alarm \
    --alarm-name "${STACK_NAME}-db-high-cpu" \
    --alarm-description "Alert when database CPU is high" \
    --metric-name CPUUtilization \
    --namespace AWS/RDS \
    --statistic Average \
    --period 300 \
    --evaluation-periods 2 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --alarm-actions $SNS_TOPIC_ARN \
    --region $REGION

aws cloudwatch put-metric-alarm \
    --alarm-name "${STACK_NAME}-db-low-storage" \
    --alarm-description "Alert when database storage is low" \
    --metric-name FreeStorageSpace \
    --namespace AWS/RDS \
    --statistic Average \
    --period 300 \
    --evaluation-periods 1 \
    --threshold 2000000000 \
    --comparison-operator LessThanThreshold \
    --alarm-actions $SNS_TOPIC_ARN \
    --region $REGION

echo ""
echo "Monitoring setup complete!"
echo "Dashboard URL: https://console.aws.amazon.com/cloudwatch/home?region=$REGION#dashboards:name=$DASHBOARD_NAME"
echo "SNS Topic ARN: $SNS_TOPIC_ARN"
echo ""
echo "Alarms created:"
echo "  - High error rate (5XX)"
echo "  - Unhealthy targets"
echo "  - High response time"
echo "  - High CPU utilization (ECS)"
echo "  - High memory utilization (ECS)"
echo "  - High database CPU"
echo "  - Low database storage"
