#!/bin/bash
set -e

ARCH=amd64
VERS=$1
CONTAINERAPPSVIEWER_NAME=imageviewer
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

  docker build . \
    -f ./Dockers/ImageView.Dockerfile \
    --build-arg REDIS_CONN_STR=$REDIS_CONN_STR \
    --build-arg REDIS_KEY=$REDIS_KEY \
    -t totosan/redis-imageviewer:$ARCH-$VERS \
    -t totosan/redis-imageviewer:$ARCH-latest
  docker push totosan/redis-imageviewer:$ARCH-$VERS && docker push totosan/redis-imageviewer:$ARCH-latest


echo "*******************************************************************************"
echo "* Container App $CONTAINERAPPSVIEWER_NAME does not exist, Creating it"
echo "*******************************************************************************"
  az containerapp create \
    --image totosan/redis-imageviewer:$ARCH-$VERS \
    --name $CONTAINERAPPSVIEWER_NAME \
    --resource-group $RESOURCE_GROUP \
    --environment $CONTAINERAPPS_ENVIRONMENT \
    --ingress external \
    --target-port 3500 \
    --transport http \
    --min-replicas 1 \
    --max-replicas 10 \
    --cpu 2.0 \
    --memory 4.0Gi \
    --enable-dapr \
    --dapr-app-port 3500 \
    --dapr-app-id imageviewer
