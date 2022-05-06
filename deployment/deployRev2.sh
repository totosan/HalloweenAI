#!/bin/bash
set -e

ARCH=amd64
VIDEO_PATH=https://youtu.be/G1VvHZ25j_k
DAPR_USED=False
VERS="poc1"

echo "Create ContainerApp Environment"
az containerapp env create \
  --name $CONTAINERAPPS_ENVIRONMENT \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --logs-workspace-id $LOG_ANALYTICS_WORKSPACE_CLIENT_ID \
  --logs-workspace-key $WSKEY

echo "Create ContainerApp"
az containerapp create \
  --image totosan/facedetection:$ARCH-$VERS \
  --name $CONTAINERAPPS_NAME \
  --resource-group $RESOURCE_GROUP \
  --environment $CONTAINERAPPS_ENVIRONMENT \
  --revision-suffix $VERS\
  --ingress external\
  --target-port 8080\
  --cpu 2.0\
  --memory 4.0Gi \
  --min-replicas 1 \
  --max-replicas 1

