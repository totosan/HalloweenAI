import redis, os, json, struct
import numpy as np
import cv2

redis_host = os.getenv("REDIS_CONN_STR", "localhost")
redis_port = 6380
redis_password = os.getenv("REDIS_KEY", "")

def saveImage(img, faceId):
    encoded=str.encode(img,encoding='ISO-8859-1')
    h, w = struct.unpack('>II',encoded[:8])
    # Add slicing here, or else the array would differ from the original
    a = np.frombuffer(encoded[8:],np.uint8)
    cv2.imwrite(f'./static/pics/{faceId}.jpg', a.reshape(h, w, 3))

def readImges():
    """Example Hello Redis Program"""
   
    # step 3: create the Redis Connection object
    try:
   
        # The decode_repsonses flag here directs the client to convert the responses from Redis into Python strings
        # using the default encoding utf-8.  This is client specific.
        r = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True,ssl=True)
        for key in r.scan_iter("*"):
            val=r.hgetall(key)
            value = json.loads(val['data'])
            saveImage(value['img'], value['face_id'])

    except Exception as e:
        print(e)

if __name__ == "__main__":
    readImges()