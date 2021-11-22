ARG VIRTUAL_ENV="/opt/venv"

FROM python:3.8-buster as builder

ARG VIRTUAL_ENV
ENV VIRTUAL_ENV=$VIRTUAL_ENV \
    PATH="$VIRTUAL_ENV/bin:$PATH"
RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get -y upgrade \
    apt-get install cmake --yes && python3 -m venv $VIRTUAL_ENV 

COPY requirements_RPI.txt ./
RUN pip install --no-cache-dir -r requirements_RPI.txt

FROM python:3.8-slim
ARG VIRTUAL_ENV
COPY --from=builder $VIRTUAL_ENV $VIRTUAL_ENV
ENV VIRTUAL_ENV=$VIRTUAL_ENV \
    PATH="$VIRTUAL_ENV/bin:$PATH"
COPY . /app/
WORKDIR /app
CMD [ "python", "main_gears.py" ]
