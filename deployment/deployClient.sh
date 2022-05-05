#!/bin/bash
set -e

ARCH=amd64
VERS="v1.0"
VIDEO_PATH=https://youtu.be/G1VvHZ25j_k
DAPR_USED=False

#override ARCH with input, if not empty
if [ ! -z "$2" ]; then
    ARCH=$2
fi

#if VERS is empty exit
if [ ! -z "$1" ]; then
    #if $1 is help, print usage
    if [ "$1" == "help" ]; then
        echo "Usage: $0 <version>"
        exit 1
    else
        VERS=$1
    fi
else
    echo "Usage: $0 <version>"
    exit 1
fi

echo "*******************************************************************************"
echo "* Deploying $VERS for $ARCH"
echo "* Docker Image: totosan/facedetection:$ARCH-$VERS"
echo "*******************************************************************************"

echo "Create docker image & push to Docker.io"

docker build . --file ./Dockers/Dockerfile-$ARCH \
--build-arg VIDEO_PATH=$VIDEO_PATH \
--build-arg DAPR_USED=$DAPR_USED \
--build-arg APP_INSIGHTS_KEY=$APP_INSIGHTS_KEY \
--tag totosan/facedetection:$ARCH-$VERS
docker push totosan/facedetection:$ARCH-$VERS


# Deployment here #######################################

if [ $(az containerapp env show -g $RESOURCE_GROUP -n $CONTAINERAPPS_ENVIRONMENT --only-show-errors --query "name" | wc -l) -eq 0 ]; then
  az containerapp env create \
    --dapr-instrumentation-key $APP_INSIGHTS_KEY \
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
    --secrets "app-insight-key=$APP_INSIGHTS_KEY" \
    --env-vars "APP_INSIGHTS_KEY=secretref:app-insight-key" \
    --ingress external\
    --target-port 8080 \
    --revision-suffix ${VERS//\./-} \
    --cpu 2.0\
    --memory 4.0Gi \
    --min-replicas 1 \
    --max-replicas 1 \
    --enable-dapr \
    --dapr-app-port 8080 \
    --dapr-app-id faceclient
