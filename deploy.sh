#!/bin/bash

# Deploy to Google Cloud Run
# Make sure you have gcloud CLI installed and authenticated

PROJECT_ID="your-project-id"
SERVICE_NAME="bank-statement-parser"
REGION="us-central1"

# Build and deploy
gcloud run deploy $SERVICE_NAME \
    --source . \
    --platform managed \
    --region $REGION \
    --project $PROJECT_ID \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 900 \
    --max-instances 10

echo "Deployment complete!"
echo "Your app will be available at: https://$SERVICE_NAME-[hash]-$REGION.a.run.app"