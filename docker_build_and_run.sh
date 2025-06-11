#!/bin/bash

# Name of your Docker image and container
IMAGE_NAME="rrgpy-streamlit"
CONTAINER_NAME="rrgpy-streamlit"

# Parse command line arguments
SKIP_BUILD=false
while getopts "s" opt; do
  case $opt in
    s)
      SKIP_BUILD=true
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      echo "Usage: $0 [-s]"
      echo "  -s: Skip build step"
      exit 1
      ;;
  esac
done

# Build the Docker image (always use latest code) unless skipped
if [ "$SKIP_BUILD" = false ]; then
  sudo docker build -t $IMAGE_NAME .
fi

# Stop and remove any existing container with the same name
sudo docker rm -f $CONTAINER_NAME 2>/dev/null

# Run the new container
sudo docker run --rm -d -p 8501:8501 --name $CONTAINER_NAME $IMAGE_NAME
