#!/bin/bash
# Script to deploy Python Code Executor to Google Cloud Run
# Date: July 25, 2025

# Exit on any error
set -e

# Configuration
PROJECT_ID="stacksyncpyexecutor"
SERVICE_NAME="python-executor"
REGION="us-central1"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud SDK (gcloud) is not installed. Please install it first."
    exit 1
fi

# Login to Google Cloud
echo "🔐 Authenticating with Google Cloud..."
gcloud auth login

# Configure Docker to use Google Cloud credentials
echo "🔄 Configuring Docker authentication..."
gcloud auth configure-docker

echo "🚀 Starting deployment process..."

# 1. Set the project
echo "Setting project to $PROJECT_ID..."
gcloud config set project $PROJECT_ID

# 2. Enable required APIs
echo "Enabling required APIs..."
gcloud services enable containerregistry.googleapis.com
gcloud services enable run.googleapis.com

# 3. Build the Docker image with AMD64 platform
echo "Building Docker image..."
docker build --platform linux/amd64 -t gcr.io/$PROJECT_ID/$SERVICE_NAME:latest .

# 4. Push to Google Container Registry
echo "Pushing image to Container Registry..."
docker push gcr.io/$PROJECT_ID/$SERVICE_NAME:latest

# 5. Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME:latest \
  --platform managed \
  --region $REGION \
  --memory 1Gi \
  --timeout 300 \
  --concurrency 1 \
  --execution-environment gen2

# 6. Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)')
echo "✅ Deployment complete!"
echo "Service URL: $SERVICE_URL"

# 7. Test the service
echo "Testing the service with a simple script..."
curl -X POST "${SERVICE_URL}/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "script": "def main():\n    return {\"message\": \"Hello from Cloud Run!\"}\n"
  }'

# Test with Fibonacci sequence
echo -e "\n\nTesting with Fibonacci sequence..."
curl -X POST "${SERVICE_URL}/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "script": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)\n\ndef main():\n    nums = [fibonacci(i) for i in range(10)]\n    return {\"fibonacci_sequence\": nums}\n"
  }'

echo -e "\n\n✨ All done! Your service is ready to use."
