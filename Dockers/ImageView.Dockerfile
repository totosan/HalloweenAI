FROM python:3.9-slim

ARG REDIS_CONN_STR
ENV REDIS_CONN_STR=$REDIS_CONN_STR
ARG REDIS_KEY
ENV REDIS_KEY=$REDIS_KEY

RUN apt update && apt -y install libgl1-mesa-glx libglib2.0-0 && rm -rf /var/lib/apt/lists/*
COPY ./src/ImageViewer ./ImageViewer/.
WORKDIR /ImageViewer
RUN pip install -r requirements.txt --no-cache-dir
CMD [ "gunicorn", "--bind", "0.0.0.0:3500", "wsgi:app" ]
