
docker run --rm --privileged multiarch/qemu-user-static --reset -p yes && \
docker buildx create --name multiarch --driver docker-container --use && \
docker buildx inspect --bootstrap

alias lastFaceAppVersion=`docker images | grep -v facedetectionapp | grep amd | awk '{print $2}' | sort | tail -n1 | cut -d '-' -f2`
alias lastFaceServerVersion=`docker images | grep facedetectionapp | grep amd | awk '{print $2}' | sort | tail -n1 | cut -d '-' -f2`