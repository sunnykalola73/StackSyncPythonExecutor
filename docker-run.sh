# Build the Docker image
docker build -t python-executor .

# Stop , rename and remove any existing container with oldername
docker stop python-executor-container || true
docker rm -f python-executor-container-old || true
docker rename python-executor-container python-executor-container-old || true

# Run the container with necessary privileges for nsjail
docker run -p 8080:8080 --name python-executor-container \
  --privileged \
  python-executor
