#!/bin/bash

# Cleanup script for Erik (Math Tutor Agent)
set -e

# 1. Configuration matches your deploy script
APP_NAME="erik-math-tutor"
REGION="us-central1"

# Get Project ID (Safe fallback)
current_project=$(gcloud config get-value project 2>/dev/null)
read -p "Enter Google Cloud Project ID [$current_project]: " PROJECT_ID
PROJECT_ID=${PROJECT_ID:-$current_project}

if [ -z "$PROJECT_ID" ]; then
    echo "❌ Error: Project ID is required."
    exit 1
fi

echo "--------------------------------------------------"
echo "🧹 Cleaning up resources for: $APP_NAME"
echo "--------------------------------------------------"

# 2. Find the Image URL *before* deleting the service
# (We need to know which image to delete)
echo "🔍 Identifying container image..."
IMAGE_URL=$(gcloud run services describe "$APP_NAME" \
    --project="$PROJECT_ID" \
    --region="$REGION" \
    --format='value(spec.template.spec.containers[0].image)' 2>/dev/null || true)

if [ -z "$IMAGE_URL" ]; then
    echo "⚠️  Service not found or already deleted."
else
    echo "found image: $IMAGE_URL"
fi

# 3. Delete the Cloud Run Service
echo "🗑️  Deleting Cloud Run service..."
gcloud run services delete "$APP_NAME" \
    --project="$PROJECT_ID" \
    --region="$REGION" \
    --quiet || echo "⚠️  Service delete failed (maybe it's already gone?)"

# 4. Delete the Container Image (Artifact Registry)
if [ -n "$IMAGE_URL" ]; then
    echo "--------------------------------------------------"
    echo "📦 Container Image Cleanup"
    echo "--------------------------------------------------"
    echo "Found image: $IMAGE_URL"
    
    read -p "Do you want to delete this image to save storage costs? (y/N) " confirm
    if [[ "$confirm" =~ ^[Yy]$ ]]; then
        echo "Deleting image..."
        # This command handles both Artifact Registry (pkg.dev) and GCR (gcr.io)
        gcloud artifacts docker images delete "$IMAGE_URL" --delete-tags --quiet
        echo "✅ Image deleted."
    else
        echo "⏭️  Skipping image deletion."
    fi
else
    echo "⚠️  Could not determine image URL automatically. Check Artifact Registry manually if needed."
fi

echo "--------------------------------------------------"
echo "✅ Cleanup Complete!"
