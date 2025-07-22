# Docker Local

## Build the Docker Image

```bash
cd traceroot-internal
export GITHUB_TOKEN=[YOUR_GITHUB_TOKEN]
export LOCAL_BUILD=true # Set to false if you want to build from the public repo
docker build --no-cache --build-arg GITHUB_TOKEN=$GITHUB_TOKEN --build-arg LOCAL_BUILD=$LOCAL_BUILD -t traceroot-public:v0.0.1 -f ./docker/public/Dockerfile .
```

## Run the Docker Container

Run the following command to start the Docker container. This one maps 3000 to the `traceroot-internal` frontend, and 8000 to the `traceroot-internal` backend.

```bash
docker run -d -p 3000:3000 -p 8000:8000 traceroot-public:v0.0.1
```
