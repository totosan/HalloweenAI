FROM balenalib/raspberrypi3-python:latest
SHELL ["/bin/sh", "-c"]

RUN apt-get update 

WORKDIR /app
COPY . .
RUN pip3 install -r requirements_RPI.txt
# Expose the port
EXPOSE 80

ENTRYPOINT [ "python3", "-u", "./main.py" ]
