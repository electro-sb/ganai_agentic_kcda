#!/bin/bash

# Deployment script for Tutor Agent to Google Cloud Run

APP_NAME="tutor-agent"
REGION="us-central1"

echo "🚀 Deploying $APP_NAME to Cloud Run..."

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI is not installed. Please install it first."
    exit 1
fi

# Check if user is authenticated
# We'll just try to run a command and see if it fails
if ! gcloud auth list &> /dev/null; then
    echo "⚠️  You might not be authenticated. Running 'gcloud auth login'..."
    gcloud auth login
fi

# Ask for Project ID if not set
PROJECT_ID=$(gcloud config get-value project)
if [ -z "$PROJECT_ID" ] || [ "$PROJECT_ID" == "(unset)" ]; then
    read -p "Enter your Google Cloud Project ID: " PROJECT_ID
    gcloud config set project "$PROJECT_ID"
fi

echo "Using Project ID: $PROJECT_ID"

# Enable necessary services
echo "Enable Cloud Run and Cloud Build APIs..."
gcloud services enable run.googleapis.com cloudbuild.googleapis.com

# Check for .env file and extract keys
if [ -f .env ]; then
    echo "Loading configuration from .env..."
    # Extract keys safely
    GOOGLE_API_KEY=$(grep "^GOOGLE_API_KEY=" .env | cut -d '=' -f2-)
    WOLFRAM_API_KEY=$(grep "^WOLFRAM_API_KEY=" .env | cut -d '=' -f2-)
    
    if [ -z "$GOOGLE_API_KEY" ] || [ -z "$WOLFRAM_API_KEY" ]; then
        echo "⚠️  Warning: GOOGLE_API_KEY or WOLFRAM_API_KEY not found in .env"
        echo "   The agent might not function correctly without them."
    fi
else
    echo "⚠️  Warning: .env file not found. Deploying without environment variables."
fi

# Deploy
# --source . builds the image using Cloud Build (no need to push local image)
# --allow-unauthenticated allows public access (for the demo)
# --set-env-vars passes the API keys
echo "Deploying..."
if gcloud run deploy "$APP_NAME" \
    --source . \
    --region "$REGION" \
    --allow-unauthenticated \
    --port 9000 \
    --set-env-vars "GOOGLE_API_KEY=$GOOGLE_API_KEY,WOLFRAM_API_KEY=$WOLFRAM_API_KEY"; then
    echo "✅ Deployment complete!"
    echo "   Visit the URL above to interact with your agent."
else
    echo "❌ Deployment failed. Please check the error messages above."
    exit 1
fi
