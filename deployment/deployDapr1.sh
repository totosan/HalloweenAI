#!/bin/bash
set -e

ARCH=amd64
VERS="dapr1"
VIDEO_PATH=https://youtu.be/G1VvHZ25j_k

# if false
if [ -n "${1}" ]; then
docker build . --file ./Dockers/Dockerfile-$ARCH \
--build-arg VIDEO_PATH=$VIDEO_PATH \
--build-arg DAPR_USED=$DAPR_USED \
--build-arg APP_INSIGHTS_KEY=$APP_INSIGHTS_KEY \
--tag totosan/facedetection:$ARCH-$VERS
docker push totosan/facedetection:$ARCH-$VERS

exit 0
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
    --min-replicas 1 \
    --max-replicas 1 \
    --enable-dapr \
    --dapr-app-port 8080 \
    --dapr-app-id faceclient
sleep 5
echo "Deployment complete"
url="https://"
fqdn=`az containerapp show -g $RESOURCE_GROUP -n $CONTAINERAPPS_NAME --query "properties.configuration.ingress.fqdn" -o tsv`
url+=$fqdn
echo "Visit $url to see the app"
