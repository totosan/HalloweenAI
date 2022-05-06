#!/bin/bash
set -e

ARCH=amd64
VERS="server1"
# if false
if [ "${1}" == "false" ]; then
  docker build . \
    -f ./Dockers/FaceApp.Dockerfile \
    --build-arg FACE_API_KEY=$FACE_API_KEY \
    --build-arg FACE_API_ENDPOINT=$FACE_API_ENDPOINT \
    -t totosan/facedetectionapp:$ARCH-$VERS 
  docker push totosan/facedetectionapp:$ARCH-$VERS
fi

echo "*******************************************************************************"
echo " Update Container Apps environment"
echo "*******************************************************************************"
az containerapp env dapr-component set \
    --name $CONTAINERAPPS_ENVIRONMENT --resource-group $RESOURCE_GROUP \
    --dapr-component-name statestore \
    --yaml ./deployment/redis.local.yaml

  az containerapp create \
    --image totosan/facedetectionapp:$ARCH-$VERS \
    --name $CONTAINERAPPSSERVER_NAME \
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
    --dapr-app-id faceserver

