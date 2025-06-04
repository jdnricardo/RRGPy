#!/bin/bash

# Name of your Docker image
IMAGE_NAME="rrgpy-streamlit"

# Name for the running container
CONTAINER_NAME="rrgpy-streamlit"

# Stop and remove any existing container with the same name
sudo docker rm -f $CONTAINER_NAME 2>/dev/null

# Run the new container
sudo docker run --rm -d -p 8501:8501 --name $CONTAINER_NAME $IMAGE_NAME
