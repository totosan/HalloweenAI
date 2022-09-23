FROM python:3.8
ARG TARGETARCH
#pip without cache
RUN pip install wheel --no-cache-dir
COPY . .
RUN ./create.sh && mv /wheelhouse /wheelhouse-$TARGETARCH 

