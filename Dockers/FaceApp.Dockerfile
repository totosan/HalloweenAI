FROM python:3.9-slim

ARG FACE_API_KEY
ARG FACE_API_ENDPOINT
ENV FACE_API_KEY=$FACE_API_KEY
ENV FACE_API_ENDPOINT=$FACE_API_ENDPOINT

RUN apt update && apt -y install libgl1-mesa-glx libglib2.0-0 && rm -rf /var/lib/apt/lists/*
COPY ./src/faceInstanceApp ./faceInstanceApp/.
COPY ./src/Tracking/. ./Tracking/.
WORKDIR /faceInstanceApp
RUN pip install -r requirements_AMD64.txt --no-cache-dir
ENV FLASK_APP=faceApi 
EXPOSE 3500
CMD [ "python", "faceApi.py" ]
