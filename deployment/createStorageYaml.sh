#!/bin/bash
RESOURCE_GROUP="MVPSession"
STORAGE_ACCOUNT="facesink001"
STORAGE_ACCOUNT_CONTAINER="facesContainer"
STORAGE_ACCOUNT_KEY="`az storage account keys list --resource-group $RESOURCE_GROUP --account-name $STORAGE_ACCOUNT --query '[0].value' --out tsv`"
DAPR_SCOPE="faceserver"

cp ./deployment/storage-template.yaml ./deployment/storage.yaml -f

#read file and replace text marked with ##STORAGE_ACCOUNT## and write to new file
sed -i "s/##STORAGE_ACCOUNT##/$STORAGE_ACCOUNT/g" ./deployment/storage.yaml
sed -i "s/##STORAGE_ACCOUNT_CONTAINER##/$STORAGE_ACCOUNT_CONTAINER/g" ./deployment/storage.yaml
sed -i "s|##STORAGE_ACCOUNT_KEY##|$STORAGE_ACCOUNT_KEY|g" ./deployment/storage.yaml
sed -i "s|##DAPR_SCOPE##|$DAPR_SCOPE|g" ./deployment/storage.yaml