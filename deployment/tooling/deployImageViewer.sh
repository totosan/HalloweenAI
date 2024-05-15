#!/bin/bash
set -e

ARCH=amd64
VERS=image1
CONTAINERAPPSVIEWER_NAME=imageviewer
#override ARCH with input, if not empty
if [ -n "${1}" ]; then
  docker build . \
    -f ./Dockers/ImageView.Dockerfile \
    --build-arg REDIS_CONN_STR=$REDIS_CONN_STR \
    --build-arg REDIS_KEY=$REDIS_KEY \
    -t totosan/redis-imageviewer:$ARCH-$VERS \
    -t totosan/redis-imageviewer:$ARCH-latest
  docker push totosan/redis-imageviewer:$ARCH-$VERS && docker push totosan/redis-imageviewer:$ARCH-latest
exit 0
fi


  az containerapp create \
    --image totosan/redis-imageviewer:$ARCH-$VERS \
    --name $CONTAINERAPPSVIEWER_NAME \
    --resource-group $RESOURCE_GROUP \
    --environment $CONTAINERAPPS_ENVIRONMENT \
    --revision-suffix ${VERS//\./-} \
    --ingress external \
    --target-port 3500 \
    --transport http \
    --min-replicas 0 \
    --max-replicas 2 \
    --cpu 2.0 \
    --memory 4.0Gi \
    --enable-dapr \
    --dapr-app-port 3500 \
    --dapr-app-id imageviewer

sleep 5
echo "Deployment complete"
url="https://"
fqdn=`az containerapp show -g $RESOURCE_GROUP -n $CONTAINERAPPSVIEWER_NAME --query "properties.configuration.ingress.fqdn" -o tsv`
url+=$fqdn
echo "Visit $url to see the app"