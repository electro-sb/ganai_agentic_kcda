#!/bin/bash

# Cloud Run Deployment Script for Erik (Math Tutor Agent)

set -e

echo "🚀 Starting deployment for Erik - Math Tutor Agent..."

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Error: gcloud CLI is not installed."
    echo "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# 1. Configuration
echo "--------------------------------------------------"
echo "📋 Configuration"
echo "--------------------------------------------------"

# Get Project ID
current_project=$(gcloud config get-value project 2>/dev/null)
read -p "Enter Google Cloud Project ID [$current_project]: " PROJECT_ID
PROJECT_ID=${PROJECT_ID:-$current_project}

if [ -z "$PROJECT_ID" ]; then
    echo "❌ Error: Project ID is required."
    exit 1
fi

# Get Region
read -p "Enter Region [us-central1]: " REGION
REGION=${REGION:-us-central1}

# Get Service Name
SERVICE_NAME="erik-math-tutor"

echo "✅ Using Project: $PROJECT_ID"
echo "✅ Using Region: $REGION"
echo "✅ Service Name: $SERVICE_NAME"

# 2. API Keys
echo "--------------------------------------------------"
echo "🔑 API Keys"
echo "--------------------------------------------------"
echo "Please enter your API keys (input will be hidden):"

read -s -p "Enter WOLFRAM_API_KEY: " WOLFRAM_KEY
echo ""
if [ -z "$WOLFRAM_KEY" ]; then
    echo "❌ Error: WOLFRAM_API_KEY is required."
    exit 1
fi

read -s -p "Enter GOOGLE_API_KEY (Gemini): " GOOGLE_KEY
echo ""
if [ -z "$GOOGLE_KEY" ]; then
    echo "❌ Error: GOOGLE_API_KEY is required."
    exit 1
fi

# 3. Deployment
echo "--------------------------------------------------"
echo "☁️  Deploying to Cloud Run..."
echo "--------------------------------------------------"

gcloud run deploy "$SERVICE_NAME" \
    --project="$PROJECT_ID" \
    --region="$REGION" \
    --source=. \
    --port=9000 \
    --allow-unauthenticated \
    --min-instances=0 \
    --max-instances=1 \
    --memory=2Gi \
    --cpu=1 \
    --set-env-vars="WOLFRAM_API_KEY=$WOLFRAM_KEY,GOOGLE_API_KEY=$GOOGLE_KEY"

echo "--------------------------------------------------"
echo "🎉 Deployment Complete!"
echo "--------------------------------------------------"
echo "You can now access Erik at the URL above."
