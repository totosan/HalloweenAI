#!/bin/bash
REDIS_NAME="facesink002"
SKU="basic"
SIZE="C0"
DAPR_SCOPE="faceserver"
RESOURCE_GROUP="MVPSession"

#create redis cache
az redis create --name $REDIS_NAME --resource-group $RESOURCE_GROUP --location "$LOCATION" --sku $SKU --vm-size $SIZE
REDIS_HOST=($(az redis show --name $REDIS_NAME --resource-group $RESOURCE_GROUP --query [hostName] --output tsv))
REDIS_PORT=($(az redis show --name $REDIS_NAME --resource-group $RESOURCE_GROUP --query [port] --output tsv))
REDIS_PORTSSL=($(az redis show --name $REDIS_NAME --resource-group $RESOURCE_GROUP --query [sslPort] --output tsv))
REDIS_PASSWORD=($(az redis list-keys --name $REDIS_NAME --resource-group $RESOURCE_GROUP --query [primaryKey] --output tsv))
REDIS_HOST=$REDIS_HOST:$REDIS_PORTSSL

cp ./deployment/redis-template.yaml ./deployment/redis.local.yaml -f

#read file and replace text marked with ##STORAGE_ACCOUNT## and write to new file
sed -i "s/##REDIS_HOST##/$REDIS_HOST/g" ./deployment/redis.local.yaml
sed -i "s/##REDIS_PASSWORD##/$REDIS_PASSWORD/g" ./deployment/redis.local.yaml
sed -i "s|##DAPR_SCOPE##|$DAPR_SCOPE|g" ./deployment/redis.local.yaml