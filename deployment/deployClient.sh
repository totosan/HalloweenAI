#!/bin/bash
set -e

ARCH=amd64
VERS="v1.0"
VIDEO_PATH=https://youtu.be/G1VvHZ25j_k

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
#if not logged in to docker, login
if [ -z "$(docker images -q totosan/facedetection:$ARCH-$VERS)" ]; then
    docker login -u totosan
fi
docker build . -f ./Dockers/Dockerfile-$ARCH --build-arg VIDEO_PATH=$VIDEO_PATH -t totosan/facedetection:$ARCH-$VERS -t totosan/facedetection:$ARCH-latest
docker push totosan/facedetection:$ARCH-$VERS
docker push totosan/facedetection:$ARCH-latest

#if containerapp already exists, delete it
if [ $(az containerapp list -g $RESOURCE_GROUP -o table | grep $CONTAINERAPPS_NAME | wc -l) -gt 0 ]; then
  az containerapp update \
    --resource-group $RESOURCE_GROUP \
    --name $CONTAINERAPPS_NAME \
    --image totosan/facedetection:$ARCH-$VERS
else
  #WSID=$(az monitor log-analytics workspace create \
  #  -g $RESOURCE_GROUP \
  #  -n $WORKSPACE_NAME \
  #  --query "customerId" -o tsv)

  az containerapp env create \
    --name $CONTAINERAPPS_ENVIRONMENT \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION #\
    #--logs-workspace-id $WSID \
    #--logs-workspace-key $WORKSPACE_KEY

  #create container app
  az containerapp create \
    --image totosan/facedetection:$ARCH-latest \
    --name $CONTAINERAPPS_NAME \
    --resource-group $RESOURCE_GROUP \
    --environment $CONTAINERAPPS_ENVIRONMENT \
    --ingress external\
    --target-port 8080\
    --cpu 2.0\
    --memory 4.0Gi \
    --min-replicas 1 \
    --max-replicas 1 \
    --enable-dapr \
    --dapr-app-port 8080 \
    --dapr-app-id faceclient

    #WSID=`az monitor log-analytics workspace show --query customerId -g $RESOURCE_GROUP -n $LOG_ANALYTICS_WORKSPACE --out tsv`
    #az monitor log-analytics query \
    #--workspace $WSID \
    #--analytics-query "ContainerAppConsoleLogs_CL | where ContainerAppName_s == 'my-container-app' | project ContainerAppName_s, Log_s, TimeGenerated | take 3" \
    #--out table
fi
