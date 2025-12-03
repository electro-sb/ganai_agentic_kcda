#!/bin/bash

# Cloud Run Deployment Script for Erik (Math Tutor Agent)
# Integrates .env loading, API enablement, and deployment.

set -e

echo "🚀 Starting deployment for Erik - Math Tutor Agent..."

# --------------------------------------------------
# 0. Prerequisites Check
# --------------------------------------------------
if ! command -v gcloud &> /dev/null; then
    echo "❌ Error: gcloud CLI is not installed."
    echo "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# --------------------------------------------------
# 1. Configuration
# --------------------------------------------------
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

# Service Name
SERVICE_NAME="erik-math-tutor"

echo "✅ Using Project: $PROJECT_ID"
echo "✅ Using Region: $REGION"
echo "✅ Service Name: $SERVICE_NAME"

# --------------------------------------------------
# 2. Enable Required APIs (One-time setup)
# --------------------------------------------------
echo "--------------------------------------------------"
echo "🛠️  Checking System Services..."
echo "--------------------------------------------------"
echo "Ensuring required Google Cloud APIs are enabled..."
echo "(This may take a few moments if they are not already active)"

gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com \
    --project="$PROJECT_ID"

echo "✅ APIs enabled."

# --------------------------------------------------
# 3. API Keys (Load from .env or Manual Input)
# --------------------------------------------------
echo "--------------------------------------------------"
echo "🔑 API Keys"
echo "--------------------------------------------------"

# Function to extract value from .env safely
get_env_value() {
    local key=$1
    if [ -f .env ]; then
        # Grep key, split at first '=', remove quotes
        grep "^${key}=" .env | cut -d '=' -f2- | tr -d '"' | tr -d "'"
    fi
}

# Attempt to load WOLFRAM_API_KEY
WOLFRAM_KEY=$(get_env_value "WOLFRAM_API_KEY")
if [ -z "$WOLFRAM_KEY" ]; then
    echo "⚠️  WOLFRAM_API_KEY not found in .env"
    read -s -p "Enter WOLFRAM_API_KEY: " WOLFRAM_KEY
    echo ""
else
    echo "✅ WOLFRAM_API_KEY loaded from .env"
fi

# Attempt to load GOOGLE_API_KEY
GOOGLE_KEY=$(get_env_value "GOOGLE_API_KEY")
if [ -z "$GOOGLE_KEY" ]; then
    echo "⚠️  GOOGLE_API_KEY not found in .env"
    read -s -p "Enter GOOGLE_API_KEY (Gemini): " GOOGLE_KEY
    echo ""
else
    echo "✅ GOOGLE_API_KEY loaded from .env"
fi

# Final Validation
if [ -z "$WOLFRAM_KEY" ] || [ -z "$GOOGLE_KEY" ]; then
    echo "❌ Error: Both API keys are required to proceed."
    exit 1
fi

# --------------------------------------------------
# 4. Deployment
# --------------------------------------------------
echo "--------------------------------------------------"
echo "☁️  Deploying to Cloud Run..."
echo "--------------------------------------------------"

# Note: --source . uses Google Cloud Buildpacks to automatically detect language.
# Ensure your app listens on port 9000 (as specified below).

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
echo "You can now access Erik at the Service URL provided above."
