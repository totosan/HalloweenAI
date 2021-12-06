FROM balenalib/armv7hf-ubuntu:bionic-build as opencv_numpy
ARG DEBIAN_FRONTEND="noninteractive"
ARG REPO_URL=https://github.com/skvark/opencv-python
ARG BRANCH=master
ARG ENABLE_CONTRIB=1

ENV LANG "C.UTF-8"
ENV LC_ALL "C.UTF-8"
ENV HOME /root
ENV PATH "/root/.pyenv/shims:/root/.pyenv/bin:$PATH"
ENV PYENV_ROOT $HOME/.pyenv
ENV PYTHON_VERSION 3.9.5
ENV ENABLE_CONTRIB ${ENABLE_CONTRIB}

#Enforces cross-compilation through Qemu
RUN [ "cross-build-start" ]

RUN install_packages \
    sudo \
    build-essential \
    ca-certificates \
    cmake \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Install pyenv
RUN git clone https://github.com/pyenv/pyenv.git $PYENV_ROOT \
    && echo 'eval "$(pyenv init -)"' >> $HOME/.bashrc

# Install Python through pyenv
RUN env PYTHON_CONFIGURE_OPTS="--enable-shared" pyenv install $PYTHON_VERSION \
    && pyenv global $PYTHON_VERSION \
    && pip3 install -U pip

# Get source code
WORKDIR /code
RUN git clone --single-branch --branch ${BRANCH} --recursive ${REPO_URL}

# Build OpenCV
WORKDIR /code/opencv-python
RUN pip wheel .
RUN [ "cross-build-end" ]


FROM balenalib/armv7hf-ubuntu-python:3.9-bionic-build as dlib
#Enforces cross-compilation through Qemu
RUN [ "cross-build-start" ]

RUN install_packages \
    sudo \
    build-essential \
    ca-certificates \
    cmake \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
RUN pip install wheel && pip wheel dlib

RUN [ "cross-build-end" ]

FROM balenalib/armv7hf-ubuntu-python:3.9-bionic-run
COPY --from=build2 /code/opencv-python/*.whl .
COPY --from=build2 /usr/lib/arm-linux-gnueabihf/ /usr/lib/
COPY --from=dlib *.whl .
COPY . .
#RUN apt install libjpeg62 libatlas3-base libbsd0
RUN /usr/local/bin/python3.9 -m pip install --upgrade pip
RUN for wheel in *.whl; do pip install $wheel; done 
RUN pip install  --no-cache-dir --find-links . -r requirements_RPI.txt --extra-index-url https://www.piwheels.org/simple --no-deps
RUN ["cross-build-end"]
