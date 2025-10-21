#!/bin/bash


set -e

ENVIRONMENT=${1:-production}

echo "Deploying to $ENVIRONMENT environment..."

if [ -f ".env.$ENVIRONMENT" ]; then
    export $(cat .env.$ENVIRONMENT | grep -v '^#' | xargs)
else
    echo "Error: .env.$ENVIRONMENT file not found"
    exit 1
fi

echo "Building Docker images..."
docker-compose -f docker-compose.prod.yml --env-file .env.$ENVIRONMENT build

echo "Stopping existing containers..."
docker-compose -f docker-compose.prod.yml --env-file .env.$ENVIRONMENT down

echo "Starting new containers..."
docker-compose -f docker-compose.prod.yml --env-file .env.$ENVIRONMENT up -d

echo "Deployment complete!"
echo "Application should be available at http://$(hostname -I | awk '{print $1}')"
