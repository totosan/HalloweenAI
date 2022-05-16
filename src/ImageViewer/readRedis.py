import redis, os, json, struct, logging, glob, sys, base64
import numpy as np
import cv2
np.set_printoptions(threshold=sys.maxsize)

redis_host = os.getenv("REDIS_CONN_STR", "localhost")
redis_port = 6380
redis_password = os.getenv("REDIS_KEY", "")

def saveImage(img, faceId):
    encoded=str.encode(img,encoding='ISO-8859-1')
    im_bytes = base64.b64decode(encoded)
    im_arr = np.frombuffer(im_bytes, dtype=np.uint8)  # im_arr is one-dim Numpy array
    img = cv2.imdecode(im_arr, flags=cv2.IMREAD_COLOR)
    cv2.imwrite(f'./static/pics/{faceId}.jpg', img)

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

def deleteAll():
    try:
        r = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True,ssl=True)
        for key in r.scan_iter("*"):
            r.delete(key)
        files= glob.glob('./static/pics/*')
        for f in files:
            os.remove(f)
    except Exception as e:
        print(e)

if __name__ == '__main__':
    readImges()