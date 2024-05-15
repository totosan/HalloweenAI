#!/bin/bash

#if LOG_ANALYTICS_WORKSPACE_CLIENT_ID already set
if [ -n "$LOG_ANALYTICS_WORKSPACE_CLIENT_ID" ]; then
    echo "LOG_ANALYTICS_WORKSPACE_CLIENT_ID already set"
else
  LOG_ANALYTICS_WORKSPACE_CLIENT_ID=`az containerapp env show --name $CONTAINERAPPS_ENVIRONMENT --resource-group $RESOURCE_GROUP --query properties.appLogsConfiguration.logAnalyticsConfiguration.customerId --out tsv`
fi
az monitor log-analytics query \
--workspace $LOG_ANALYTICS_WORKSPACE_CLIENT_ID \
--analytics-query "ContainerAppConsoleLogs_CL  | project TimeGenerated, _timestamp_d, ContainerName_s, Log_s | order by _timestamp_d desc | take 10" \
--out table
