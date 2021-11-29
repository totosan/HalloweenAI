FROM balenalib/raspberrypi3-python:3.9-bullseye 
RUN ["cross-build-start"]
RUN install_packages wget \
    cmake gfortran libgfortran5 \
    build-essential unzip git \
    python3-all-dev \
    libjpeg-dev libtiff-dev libgif-dev \
    libavcodec-dev libavformat-dev libswscale-dev \
    libgtk2.0-dev libcanberra-gtk* \
    libxvidcore-dev libx264-dev libgtk-3-dev \
    libtbb2 libtbb-dev libdc1394-22-dev libv4l-dev \
    libopenblas-dev \
    libatlas3-base libgfortran3 libice6 libsm6 \
    libjasper-dev liblapack-dev libhdf5-dev \
    v4l-utils libgoogle-glog-dev libgflags-dev libprotobuf-dev \
    protobuf-compiler 
RUN python -m pip install --upgrade pip numpy==1.21.4
RUN cd /usr/local/lib/python3.10/site-packages/ && \
    ls -alh &&\
    ln -s /usr/lib/python3/dist-packages/cv2.cpython-39-arm-linux-gnueabihf.so ./cv2.so
RUN cd / 
COPY . .
RUN pip install -r requirements_RPI.txt
RUN ["cross-build-end"]