#!/bin/bash

apps=$(az containerapp list -g $RESOURCE_GROUP --query "[].name" -o tsv)
echo $apps | while IFS= read -r line; do 
    echo "Deleting $line"
    az containerapp delete -g $RESOURCE_GROUP -n $line --yes
done

echo "Delete ContainerApp Environment"
az containerapp env delete -g $RESOURCE_GROUP -n $CONTAINERAPPS_ENVIRONMENT --yes
