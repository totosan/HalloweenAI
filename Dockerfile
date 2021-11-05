FROM arm32v7/python
SHELL ["/bin/sh", "-c"]

RUN apt-get update && apt-get update 

WORKDIR /app
COPY . .
RUN pip3 install -r requirements_RPI.txt
# Expose the port
EXPOSE 80

CMD [ "python3", "-u", "./main.py" ]
