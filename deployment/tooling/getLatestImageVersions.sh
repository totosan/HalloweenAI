export APPVERS=$(docker images | grep -v facedetectionapp | grep amd | awk '{print $2}' | sort | tail -n1 | cut -d '-' -f2)
echo "App $APPVERS"
export SERVERVERS=$(docker images | grep facedetectionapp | grep amd | awk '{print $2}' | sort | tail -n1 | cut -d '-' -f2)
echo "Server $SERVERVERS"