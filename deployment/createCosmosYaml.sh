#!/bin/bash
RESOURCE_GROUP="MVPSession"
COSMOS_ACCOUNT="facesink001"
COSMOS_DATABASE="facesdb"
COSMOS_CONTAINER="facesink"

# Create a free tier account for SQL API
az cosmosdb create \
    -n $COSMOS_ACCOUNT \
    -g $RESOURCE_GROUP \
    --location regionName=$LOCATION \
    --default-consistency-level "Session"

az cosmosdb sql database create \
    --account-name $COSMOS_ACCOUNT \
    --resource-group $RESOURCE_GROUP \
    --name $COSMOS_DATABASE

az cosmosdb sql container create \
  --account-name $COSMOS_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --database-name $COSMOS_DATABASE \
  --name $COSMOS:CONTAINER \
  --throughput 400 

COSMOS_URL="https://$COSMOS_ACCOUNT.documents.azure.com:443/"

#get cosmosdb primary key
MASTER_KEY=$(az cosmosdb list-keys --name $COSMOS_ACCOUNT --resource-group $RESOURCE_GROUP --query primaryMasterKey -o tsv)
DAPR_SCOPE="faceserver"

cp ./deployment/cosmos-template.yaml ./deployment/cosmos.local.yaml -f

#read file and replace text marked with ##STORAGE_ACCOUNT## and write to new file
sed -i "s/##COSMOS_URL##/$COSMOS_URL/g" ./deployment/cosmos.local.yaml
sed -i "s/##COSMOS_ACCOUNT##/$COSMOS_ACCOUNT/g" ./deployment/cosmos.local.yaml
sed -i "s|##COSMOS_CONTAINER##|$COSMOS_CONTAINER|g" ./deployment/cosmos.local.yaml
sed -i "s|##MASTER_KEY##|$MASTER_KEY|g" ./deployment/cosmos.local.yaml
sed -i "s|##DAPR_SCOPE##|$DAPR_SCOPE|g" ./deployment/cosmos.local.yaml