#!/bin/bash
set -e

ARCH=amd64
VERS="server2"
# if false
if [ -n "${1}" ]; then
  docker build . \
    -f ./Dockers/FaceApp.Dockerfile \
    --build-arg FACE_API_KEY=$FACE_API_KEY \
    --build-arg FACE_API_ENDPOINT=$FACE_API_ENDPOINT \
    -t totosan/facedetectionapp:$ARCH-$VERS 
  docker push totosan/facedetectionapp:$ARCH-$VERS
  exit 0
fi

echo "*******************************************************************************"
echo " Update Container Apps environment"
echo "*******************************************************************************"

  az containerapp create \
    --image totosan/facedetectionapp:$ARCH-$VERS \
    --name $CONTAINERAPPSSERVER_NAME \
    --resource-group $RESOURCE_GROUP \
    --environment $CONTAINERAPPS_ENVIRONMENT \
    --env-vars "FACEAPI_USED=True" \
    --revision-suffix $VERS \
    --ingress external \
    --target-port 3000 \
    --transport http \
    --min-replicas 1 \
    --max-replicas 10 \
    --cpu 2.0 \
    --memory 4.0Gi \
    --enable-dapr \
    --dapr-app-port 3000 \
    --dapr-app-id faceserver

