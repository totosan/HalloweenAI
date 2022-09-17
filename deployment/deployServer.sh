#!/bin/bash
set -e

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
echo "*******************************************************************************"
#if not logged in to docker, login
if [ -z "$(docker images -q totosan/facedetectionapp:amd64-latest)" ]; then
    docker login -u totosan
fi


if [ $ARCH == "arm64" ]; then
  docker buildx build \
    --platform linux/$ARCH \
    --build-arg FACE_API_KEY=$FACE_API_KEY \
    --build-arg FACE_API_ENDPOINT=$FACE_API_ENDPOINT \
    -f ./Dockers/FaceApp.Dockerfile \
    -t totosan/facedetectionapp:$ARCH-$VERS \
    -t totosan/facedetectionapp:$ARCH-latest \
    --load \
    .
  docker push totosan/facedetectionapp:$ARCH-$VERS && docker push totosan/facedetectionapp:$ARCH-latest
  exit 1
else
  docker build . \
    -f ./Dockers/FaceApp.Dockerfile \
    --build-arg FACE_API_KEY=$FACE_API_KEY \
    --build-arg FACE_API_ENDPOINT=$FACE_API_ENDPOINT \
    -t totosan/facedetectionapp:$ARCH-$VERS \
    -t totosan/facedetectionapp:$ARCH-latest
  docker push totosan/facedetectionapp:$ARCH-$VERS && docker push totosan/facedetectionapp:$ARCH-latest
fi

echo "*******************************************************************************"
echo " Update Container Apps environment"
echo "*******************************************************************************"
az containerapp env dapr-component set \
    --name $CONTAINERAPPS_ENVIRONMENT --resource-group $RESOURCE_GROUP \
    --dapr-component-name statestore \
    --yaml ./deployment/redis.local.yaml

#create container app
if [ $VERS == "latest" ]; then
  echo "Deleting Container App, because of lable latest"
    az containerapp delete -g $RESOURCE_GROUP -n $CONTAINERAPPSSERVER_NAME -y
    sleep 10
fi


echo "*******************************************************************************"
echo "* Container App $CONTAINERAPPSSERVER_NAME "
echo "*******************************************************************************"
  az containerapp create \
    --image totosan/facedetectionapp:$ARCH-$VERS \
    --name $CONTAINERAPPSSERVER_NAME \
    --resource-group $RESOURCE_GROUP \
    --environment $CONTAINERAPPS_ENVIRONMENT \
    --env-vars "FACEAPI_USED=True" \
    --ingress external \
    --target-port 3000 \
    --transport http \
    --min-replicas 0 \
    --max-replicas 10 \
    --cpu 2.0 \
    --memory 4.0Gi \
    --enable-dapr \
    --dapr-app-port 3000 \
    --dapr-app-id faceserver
