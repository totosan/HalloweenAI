FROM python:3.9-slim
RUN apt update 
COPY faceDetectApp .
RUN pip install flask dapr requests --no-cache-dir
ENV FLASK_APP=faceApi 
EXPOSE 3500
CMD [ "python", "faceApi.py" ]
