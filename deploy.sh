#!/bin/bash

# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# Cloud Run Deployment Script
# Usage: ./deploy.sh [PROJECT_ID] [REGION]

# 1. Configuration
APP_NAME="cv-vipassana-app"
DEFAULT_REGION="us-central1"

# 2. Argument Parsing
PROJECT_ID=$1
REGION=${2:-$DEFAULT_REGION}

if [ -z "$PROJECT_ID" ]; then
    echo "Error: Project ID is required."
    echo "Usage: ./deploy.sh <PROJECT_ID> [REGION]"
    exit 1
fi

# 3. Generate a random Secret Key for Flask Session security
SECRET_KEY=$(openssl rand -hex 32)

echo "=================================================="
echo "Deploying $APP_NAME to Google Cloud Run"
echo "Project: $PROJECT_ID"
echo "Region:  $REGION"
echo "=================================================="

# 4. Enable necessary APIs (Idempotent)
echo "Enabling necessary APIs..."
gcloud services enable run.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com \
    aiplatform.googleapis.com \
    bigquery.googleapis.com \
    --project "$PROJECT_ID"

# 5. Deploy
# This uses source deployment (Cloud Buildpacks) to build the container automatically
# from the requirements.txt and app.py files.
echo "Deploying to Cloud Run..."
gcloud run deploy "$APP_NAME" \
    --source . \
    --project "$PROJECT_ID" \
    --region "$REGION" \
    --platform managed \
    --allow-unauthenticated \
    --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID" \
    --set-env-vars "LOCATION=$REGION" \
    --set-env-vars "SECRET_KEY=$SECRET_KEY" \
    --memory 1Gi

echo "=================================================="
echo "Deployment Complete!"
echo "=================================================="