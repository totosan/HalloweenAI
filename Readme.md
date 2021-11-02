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