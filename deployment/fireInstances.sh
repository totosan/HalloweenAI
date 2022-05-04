URL=https://facedetection-app.wittyocean-e3f0ab1e.westeurope.azurecontainerapps.io/video
for i in {1..10}; do
curl -X GET $URL  &
done