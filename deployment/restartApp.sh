#!/bin/bash
# restart facedetection app
REVS=`az containerapp revision list -n $CONTAINERAPPS_NAME -g $RESOURCE_GROUP --query "[].{Revision:name}" -o tsv`
#echo "Restarting $REVS"
for REV in $REVS; do
    az containerapp revision restart --revision $REV --resource-group $RESOURCE_GROUP
done
