#!/bin/bash
# restart facedetection app
fqdn=`az containerapp show -g $RESOURCE_GROUP -n $CONTAINERAPPS_NAME --query "properties.configuration.ingress.fqdn" -o tsv`
url="https://$fqdn/restart"
curl $url
REV=`az containerapp show -g $RESOURCE_GROUP --name $CONTAINERAPPS_NAME --query "properties.latestRevisionName" -o tsv`
echo "Restarting $REV"
az containerapp revision restart --revision $REV --resource-group $RESOURCE_GROUP