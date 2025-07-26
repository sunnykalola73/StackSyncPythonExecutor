# Python Secure Code Execution API

A Flask-based API service that securely executes arbitrary Python code using nsjail for sandboxing.

> Note: The app is hosted on GCP url(`https://python-executor-378957403805.us-central1.run.app`)

## API Endpoints

### POST /execute

Executes Python code and returns the result of the `main()` function.

**Request Body:**
```json
{
  "script": "def main():\n    return {'hello': 'world'}"
}
```

**Response:**
```json
{
  "result": {"hello": "world"},
  "stdout": ""
}
```

**Error Response:**
```json
{
  "error": "Error message",
  "stdout": "any print output",
  "stderr": "any error output"
}
```

## Configuration

The service can be configured using environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 8080 | Server port |
| `HOST` | 0.0.0.0 | Server host |
| `MAX_CODE_LENGTH` | 10000 | Maximum code length in characters |
| `EXECUTION_TIMEOUT` | 30 | Code execution timeout in seconds |
| `MEMORY_LIMIT_MB` | 512 | Memory limit in MB |
| `CPU_LIMIT_SEC` | 10 | CPU time limit in seconds |
| `FILE_SIZE_LIMIT_MB` | 16 | File size limit in MB |
| `MAX_FILES` | 32 | Maximum number of files |

## Requirements

- Python code must contain a `main()` function
- The `main()` function should return JSON-serializable data
- Code execution is limited to 30 seconds
- Memory usage is limited to 512MB

### Prerequisites

- Docker
- Python 3.11+

### Running with Docker

use the provided script:

```bash
chmod +x docker-run.sh
./docker-run.sh
```

### Example Usage

#### Example-1
```
curl --location 'https://python-executor-378957403805.us-central1.run.app/execute' \
--header 'Content-Type: application/json' \
--data '{
    "script": "def main():\n    print('\''Executing Hello World script'\'')\n    return {'\''message'\'': '\''Hello World'\'', '\''status'\'': '\''success'\''}"
}'
```
#### Example-2
```
curl -X POST https://python-executor-378957403805.us-central1.run.app/execute -H "Content-Type: application/json" -d '{"script": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)\n\ndef main():\n    nums = [fibonacci(i) for i in range(10)]\n    return {\"fibonacci_sequence\": nums}\n"}'
```


## Deployment

### Google Cloud Run

1. Build and push to Container Registry:
```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/python-executor
```

2. Deploy to Cloud Run:
```bash
gcloud run deploy python-executor \
  --image gcr.io/YOUR_PROJECT_ID/python-executor \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 512Mi \
  --cpu 1 \
  --timeout 60s
```
