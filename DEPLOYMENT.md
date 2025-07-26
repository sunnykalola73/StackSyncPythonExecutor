# Deploying Python Code Executor to Google Cloud Run

This document outlines the steps to deploy the Python Code Executor service to Google Cloud Run.

## Prerequisites

1. Install Google Cloud SDK
2. Install Docker
3. Authenticate with Google Cloud:
   ```bash
   # Login to Google Cloud
   gcloud auth login

   # Configure Docker to use Google Cloud credentials
   gcloud auth configure-docker
   ```
4. Enable required Google Cloud APIs:
   ```bash
   gcloud services enable containerregistry.googleapis.com
   gcloud services enable run.googleapis.com
   ```

## Steps

### 1. Configure Google Cloud Project

```bash
# Set your project ID
export PROJECT_ID="stacksyncpyexecutor"
gcloud config set project $PROJECT_ID
```

### 2. Build the Docker Image

```bash
# Build the image with AMD64 platform for Cloud Run
docker build --platform linux/amd64 -t gcr.io/$PROJECT_ID/python-executor:latest .
```

### 3. Push to Google Container Registry

```bash
# Push the image to GCR
docker push gcr.io/$PROJECT_ID/python-executor:latest
```

### 4. Deploy to Cloud Run

```bash
# Deploy the service
gcloud run deploy python-executor \
  --image gcr.io/$PROJECT_ID/python-executor:latest \
  --platform managed \
  --region us-central1 \
  --memory 1Gi \
  --timeout 300 \
  --concurrency 1 \
  --execution-environment gen2
```

## Usage

Once deployed, you can use the service by sending POST requests to the execution endpoint:

```bash
curl -X POST https://python-executor-[YOUR-PROJECT-NUMBER].us-central1.run.app/execute \
  -H "Content-Type: application/json" \
  -d '{
    "script": "def main():\n    return {\"message\": \"Hello from Cloud Run!\"}\n"
  }'
```

### Example Response

```json
{
  "result": {
    "message": "Hello from Cloud Run!"
  },
  "stdout": ""
}
```

## Configuration

### Environment Variables
The service can be configured using environment variables:

- `MAX_CODE_LENGTH`: Maximum length of code in characters (default: 10000)
- `EXECUTION_TIMEOUT`: Maximum execution time in seconds (default: 30)
- `PORT`: Server port (default: 8080)
- `HOST`: Server host (default: 0.0.0.0)

### Authentication
To update or reauthenticate:

```bash
# Login to Google Cloud (if session expired)
gcloud auth login

# Configure Docker authentication (if needed)
gcloud auth configure-docker

# Verify authentication
gcloud auth list
gcloud config list
```

### Project Configuration
You can check and update your project configuration:

```bash
# List your projects
gcloud projects list

# Set your active project
gcloud config set project YOUR_PROJECT_ID

# Verify current configuration
gcloud config get-value project
```

## Security Notes

The service uses several security measures:

1. Process isolation through nsjail
2. Memory and CPU limits through Cloud Run resources
3. Network isolation through Cloud Run's security model
4. Input code validation
5. JSON serialization checks on output

## Monitoring and Logging

You can monitor the service through Google Cloud Console:
- Cloud Run dashboard
- Cloud Logging
- Cloud Monitoring

## Troubleshooting

If you encounter issues:

1. Check Cloud Run logs for error messages
2. Verify the container can start locally:
   ```bash
   docker run -p 8080:8080 gcr.io/$PROJECT_ID/python-executor:latest
   ```
3. Test the service locally before deploying:
   ```bash
   curl -X POST http://localhost:8080/execute -H "Content-Type: application/json" \
     -d '{"script": "def main():\n    return {\"test\": True}\n"}'
   ```
