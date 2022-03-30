## Project setup

- create environment vars like step below
- create .env file with key/values
    - FACE_API_KEY (key from Azure portal to access Face API)
    - FACE_API_ENDPOINT (endpoint url from Azure portal)
    - VIDEO_PATH (you can choose from several inputs: Youtube, RTSP, WebCam)
- you can use below statement to set env vars in system from **.env** file
```
export $(grep -v '^#' .env | xargs -d '\n')
```
- I suggest creating a virtual env

## Running Docker buildx fpr arm32v7
If you have any issues building the docker image for ARM32v7...   
Error could be:   
*rpc error: code = Unknown desc = process "/dev/.buildkit_qemu_emulator*

https://github.com/docker/buildx/issues/495

```
docker run --rm --privileged multiarch/qemu-user-static --reset -p yes
docker buildx create --name multiarch --driver docker-container --use
docker buildx inspect --bootstrap
```

## Building Dockerfile
```
docker buildx build --platform linux/arm/v7 -t totosan/facedetection:latest --load .
```

### Issues with building Docker and OpenCV, DLib
- opencv is build in a dev-stage of the dockerfile with the version 4.5.4.35 as wheel
- also numpy 19.22.1 is build as wheel
- creating the final stage copies those wheels, created in the dev stage, and installes those (opencv, numpy)
- with pip install -r requirements_RPi.txt also dlib is installed - this claims for missing shared libs   
--> so here is how to get arround this
so you have to use ldd and apt-file to get things done:

- find **_dlib_pybind11.cpython-39-arm-linux-gnueabihf.so**

`> ldd _dlib_pybind11.cpython-39-arm-linux-gnueabihf.so | grep "not found"`
```
./_dlib_pybind11.cpython-39-arm-linux-gnueabihf.so: /lib/arm-linux-gnueabihf/libm.so.6: version `GLIBC_2.29' not found (required by ./_dlib_pybind11.cpython-39-arm-linux-gnueabihf.so)
./_dlib_pybind11.cpython-39-arm-linux-gnueabihf.so: /usr/lib/arm-linux-gnueabihf/libstdc++.so.6: version `GLIBCXX_3.4.26' not found (required by ./_dlib_pybind11.cpython-39-arm-linux-gnueabihf.so)
        libjpeg.so.62 => not found
        libcblas.so.3 => not found
        liblapack.so.3 => not found
        libbsd.so.0 => not found
```
- then take e.g. libjpeg.so.62
    - `> apt-file search libjpeg.so.62`
    ```
    libjpeg62: /usr/lib/arm-linux-gnueabihf/libjpeg.so.62
    libjpeg62: /usr/lib/arm-linux-gnueabihf/libjpeg.so.62.0.0
    ```
    - so we know now, that we also should install **libjpeg62**
    - apt install libjpeg62
- continue with all other.