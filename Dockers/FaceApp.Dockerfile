FROM python:3.9-alpine
RUN apk update 
COPY faceDetectApp .
RUN pip install flask requests
ENV FLASK_APP=faceApi 
EXPOSE 3500
CMD [ "python", "faceApi.py" ]
