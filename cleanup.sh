#!/bin/bash

# Cleanup script for Tutor Agent resources

APP_NAME="tutor-agent"
REGION="us-central1"

echo "🧹 Cleaning up Cloud Run resources for $APP_NAME..."

# 1. Delete the Cloud Run Service
echo "Deleting Cloud Run service..."
gcloud run services delete "$APP_NAME" --region "$REGION" --quiet

# 2. Delete the Container Images (Optional but recommended to save storage costs)
# This finds the image repository associated with the service
echo "Deleting container images..."
IMAGE_PATH="gcr.io/$(gcloud config get-value project)/$APP_NAME"
# Note: Cloud Build might store images in a different path depending on configuration
# Usually it's gcr.io/PROJECT_ID/app_name or similar. 
# A safer way is to list images and delete them.

echo "⚠️  To delete the container images, go to the Container Registry or Artifact Registry in Google Cloud Console."
echo "   Or run: gcloud container images delete gcr.io/$(gcloud config get-value project)/$APP_NAME --force-delete-tags --quiet"

echo "✅ Service deleted! You won't be charged for the running service anymore."
