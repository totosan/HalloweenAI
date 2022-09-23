# docker buildx build --push --platform linux/arm64/v8,linux/amd64 -t iotcontainertt.azurecr.io/tracking-py:latest .
FROM python:3.8
ARG TARGETARCH
#pip without cache
RUN pip install wheel --no-cache-dir
COPY . .
RUN ./create.sh && mv /wheelhouse /wheelhouse-$TARGETARCH 
