# Prerequisits #

## extend **az** tools with containerapp
- $ `az extension add -n containerapp`

## add ContainerApp Environment ##
```
az containerapp env create -n $CONTAINERAPPS_ENVIRONMENT -g $RESOURCE_GROUP -l $LOCATION
```

## add ContainerApp itself ##
```
az containerapp create --image totosan/facedetection:amd64-latest -n $CONTAINERAPPS_NAME --environment $CONTAINERAPPS_ENVIRONMENT -g $RESOURCE_GROUP --ingress external --target-port 8080
```