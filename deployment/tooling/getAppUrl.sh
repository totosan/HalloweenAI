#!/bin/bash
fqdn=`az containerapp show -g $RESOURCE_GROUP -n $CONTAINERAPPS_NAME --query "properties.latestRevisionFqdn" -o tsv`
echo https://$fqdn/