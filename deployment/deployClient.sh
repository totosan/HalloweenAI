#!/bin/bash
set -e

ARCH=amd64
VERS="poc"
VIDEO_PATH=https://youtu.be/G1VvHZ25j_k
DAPR_USED=False
INC=1

echo "*******************************************************************************"
echo "* Deploying $VERS for $ARCH"
echo "* Docker Image: totosan/facedetection:$ARCH-$VERS"
echo "*******************************************************************************"

echo "Create docker image & push to Docker.io"

docker build . --file ./Dockers/Dockerfile-$ARCH \
--build-arg VIDEO_PATH=$VIDEO_PATH \
--tag totosan/facedetection:$ARCH-$VERS
docker push totosan/facedetection:$ARCH-$VERS

# Deployment here #######################################

if [ $(az containerapp env show -g $RESOURCE_GROUP -n $CONTAINERAPPS_ENVIRONMENT --query "name" | wc -l) -eq 0 ]; then
  az containerapp env create \
    --name $CONTAINERAPPS_ENVIRONMENT \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --logs-workspace-id $LOG_ANALYTICS_WORKSPACE_CLIENT_ID \
    --logs-workspace-key $WSKEY
fi

#create container app
az containerapp create \
  --image totosan/facedetection:$ARCH-$VERS \
  --name $CONTAINERAPPS_NAME \
  --resource-group $RESOURCE_GROUP \
  --environment $CONTAINERAPPS_ENVIRONMENT \
  --revision-suffix $( expr $INC + 1 ) \
  --ingress external\
  --target-port 8080\
  --cpu 2.0\
  --memory 4.0Gi \
  --min-replicas 1 \
  --max-replicas 1

