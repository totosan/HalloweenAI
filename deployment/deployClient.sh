#!/bin/bash
set -e

ARCH=amd64
VERS="app"
VIDEO_PATH=https://youtu.be/G1VvHZ25j_k
DAPR_USED=True

#override ARCH with input, if not empty
if [ ! -z "$2" ]; then
    ARCH=$2
fi

#if VERS is empty exit
if [ ! -z "$1" ]; then
    
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

fi

# Deployment here #######################################

  az containerapp env create \
    --dapr-instrumentation-key $APP_INSIGHTS_KEY \
    --name $CONTAINERAPPS_ENVIRONMENT \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --logs-workspace-id $LOG_ANALYTICS_WORKSPACE_CLIENT_ID \
    --logs-workspace-key $WSKEY

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
    --min-replicas 0 \
    --max-replicas 1 \
    --enable-dapr \
    --dapr-app-port 8080 \
    --dapr-app-id faceclient

watch -n 1 az containerapp logs show --name $CONTAINERAPPS_NAME --resource-group $RESOURCE_GROUP

