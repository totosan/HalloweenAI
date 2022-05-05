#!/bin/bash
# restart facedetection app
REV=`az containerapp show -g $RESOURCE_GROUP --name $CONTAINERAPPS_NAME --query "properties.latestRevisionName" -o tsv`
echo "Restarting $REV"
az containerapp revision restart --revision $REV --resource-group $RESOURCE_GROUP