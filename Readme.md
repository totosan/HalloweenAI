# Facedetection Solution
## About
This project is a kind of proof of several technologies:
- AI: DNN with OpenCV
- Dockerization
- Modular Video capture (RTSP, Youtube, WebCam,...)
- Video analysis capabilities by injecting facedetection
- hosting locally with container
- hosting in Azure Container Apps (ACA)
- CI/CD GitHub Actions
- different platform targets (amd64/ arm64)
- ...

This project reads a video stream and detects faces with a neural network by using opencv



This project contains a video capture and processing app (often called facedetection app) and a face processing service (often called facedetection server app).
For a local run, the face processing service cannot be deployed, because it is currently designed for running in Azure container apps. But it is no magic, to get this also running locally. Just modify the FaceApp.Dockerfile to your specific underlying platform architecture and install DAPR & Redis. 

## Project setup
This project targets **MS Azure** as cloud backend. So make sure, if you want to try the ACA-Solution, that you have access to a subscription with Contributer role for example


- create environment vars like step below
- create .env file with key/values
    generally needed vars
    - FACE_API_KEY *(key from Azure portal to access Face API)*
    - FACE_API_ENDPOINT *(endpoint url from Azure portal)*
    - VIDEO_PATH *(you can choose from several inputs: Youtube, RTSP, WebCam)*
    - DAPR_USED *(if you deploy to ACA, sset to true, if locally, set to false)*
    
    Azure deployment needed vars
    - RESOURCE_GROUP *(Azure Resource group name)*
    - LOCATION *(the region to deploy to)*
    - CONTAINERAPPS_ENVIRONMENT *(the ACA environment name)*
    - CONTAINERAPPS_NAME *(name of the video client application name in the ACA environment)*
    - CONTAINERAPPSSERVER_NAME *(name of the detected faces consuming application in ACA env.)*
    
    for use with GH Actions
    - SP_ID *(Service principle ID)*
    - SP_NAME *(Service principle name)*
    - SP_SECRET *(Service principal secret)*
    - SP_TENANT *(tenent id, where service principal has been created in)*
    - DOCKER_USER *(Docker registry username)*
    - DOCKER_PWD *(Docker registry password)*

- you can use below statement to set env vars in system from **.env** file
- TIP: just create .local.env file as copy from .env!! All files with '.local.' (see .gitignore) will be ignored from git commit. So your credentials resides just locally.
```
export $(grep -v '^#' .env | xargs -d '\n')
```
- I suggest creating a virtual env, if you work with this on your local equipment.
- You should consider to use Codespaces from this repo. A **.devcontainerjson** is configured.

## Running Docker buildx for various "foreign" architectures like armXX
If you have any issues building the docker image for ARM32v7/...   
Error could be:   
*rpc error: code = Unknown desc = process "/dev/.buildkit_qemu_emulator*

https://github.com/docker/buildx/issues/495

The following lines are part ov **.devcontainer.json**

```
docker run --rm --privileged multiarch/qemu-user-static --reset -p yes
docker buildx create --name multiarch --driver docker-container --use
docker buildx inspect --bootstrap
```

## Building & pushing Dockerfile
1. facedetection video app
```
ARCH=arm64
docker buildx build --platform linux/$ARCH -f ./Dockers/Dockerfile-$ARCH -t totosan/facedetection:$ARCH-latest --load .
docker push totosan/facedetection:$ARCH-latest
```

2. facedetection processor server
```
ARCH=amd64
docker buildx build --platform linux/$ARCH -f ./Dockers/FaceApp.Dockerfile -t totosan/facedetectionapp:$ARCH-latest --load .
docker push totosan/facedetectionapp:$ARCH-latest
```

## Decide, whether it is a locally hosted app or ACA
### In case of ACA
For running the solution as ACA enabled, there must be an environment variable called DAPR_USED with value 'true'.
This enables video processing module (facedetection app) to send detections to seperate service, that saves it's states to a redis cache
<image src="./assets/architecture.png"/>

### In case of local docker hosting
Just create the docker image from the files in **'Dockers' folder** and consume it, where you like.   
Make sure, to pass the environment variables described above, that are needed in general.   

### different setup with Kubernetes
If you're more used to have K8s running, you can stick to the installation process of DAPR with K8s and deploy the solution locally.   
I have to mention, that for time writing, there some differences in deployment and consumation of services compared to ACA.
For example, the schema of yaml file, I used for setup of redis cache as statestore is different.


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