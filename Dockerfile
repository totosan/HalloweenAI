FROM balenalib/raspberrypi3-python:3.9-bullseye 
RUN ["cross-build-start"]
RUN install_packages wget \
    cmake gfortran \
    build-essential unzip git \
    python3-all-dev \
    libjpeg-dev libtiff-dev libgif-dev \
    libavcodec-dev libavformat-dev libswscale-dev \
    libgtk2.0-dev libcanberra-gtk* \
    libxvidcore-dev libx264-dev libgtk-3-dev \
    libtbb2 libtbb-dev libdc1394-22-dev libv4l-dev \
    libopenblas-dev libatlas3-base libice6 libsm6 \
    libjasper-dev liblapack-dev libhdf5-dev \
    v4l-utils libgoogle-glog-dev libgflags-dev libprotobuf-dev \
    protobuf-compiler libopenexr-dev
COPY . .
RUN pip install -r requirements_RPI.txt --extra-index-url https://www.piwheels.org/simple
RUN ["cross-build-end"]