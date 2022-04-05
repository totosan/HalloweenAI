#!/bin/bash
set -e

RESOURCE_GROUP="MVPSession"
LOCATION="westeurope"
CONTAINERAPPS_ENVIRONMENT="ai-tt-env"
CONTAINERAPPSSERVER_NAME="facedetection-server"

ARCH=amd64
VERS=$1

#override ARCH with input, if not empty
if [ ! -z "$2" ]; then
    ARCH=$2
fi

#if VERS is empty exit
if [ -z "$VERS" ]; then
  echo "Usage: $0 <version>"
  exit 1
fi

echo "*******************************************************************************"
echo "* Deploying $VERS for $ARCH"
echo "*******************************************************************************"

echo "Create docker image & push to Docker.io"
#if not logged in to docker, login
if [ -z "$(docker images -q totosan/facedetection:$ARCH-$VERS)" ]; then
    docker login -u totosan
fi
if [ $ARCH == "arm64" ]; then
  docker buildx build --platform linux/$ARCH -f ./Dockers/FaceApp.Dockerfile -t totosan/facedetectionapp:$ARCH-$VERS -t totosan/facedetectionapp:$ARCH-latest --load .
  docker push totosan/facedetectionapp:$ARCH-$VERS && docker push totosan/facedetectionapp:$ARCH-latest
  exit 1
else
  docker build . -f ./Dockers/FaceApp.Dockerfile -t totosan/facedetectionapp:$ARCH-$VERS -t totosan/facedetectionapp:$ARCH-latest
  docker push totosan/facedetectionapp:$ARCH-$VERS && docker push totosan/facedetectionapp:$ARCH-latest
fi

az containerapp env dapr-component set \
    --name $CONTAINERAPPS_ENVIRONMENT --resource-group $RESOURCE_GROUP \
    --dapr-component-name statestore \
    --yaml ./deployment/storage.local.yaml

#create container app
#if containerapp already exists, delete it
if [ $(az containerapp list -g $RESOURCE_GROUP -o table | grep $CONTAINERAPPSSERVER_NAME | wc -l) -gt 0 ]; then
  az containerapp update \
    --resource-group $RESOURCE_GROUP \
    --name $CONTAINERAPPSSERVER_NAME \
    --image totosan/facedetectionapp:$ARCH-$VERS
else
  az containerapp create \
    --image totosan/facedetectionapp:$ARCH-$VERS \
    --name $CONTAINERAPPSSERVER_NAME \
    --resource-group $RESOURCE_GROUP \
    --environment $CONTAINERAPPS_ENVIRONMENT \
    --ingress external \
    --target-port 3500 \
    --transport http \
    --min-replicas 1 \
    --max-replicas 1 \
    --cpu 2.0 \
    --memory 4.0Gi \
    --enable-dapr \
    --dapr-app-port 3500 \
    --dapr-app-id faceserver
  fi