import sys

from itsdangerous import base64_decode, base64_encode
sys.path.append("../")
sys.path.append("../Tracking/")

from crypt import methods
from distutils.log import debug
import io, os, requests, json
import struct
from itertools import count
from datetime import datetime
from urllib import response

from flask import Flask, request, jsonify
from dapr.clients import DaprClient
from PIL import Image
import logging 
import numpy
from Tracking.FaceAPI import FaceDetection

try:
    import ptvsd
    ptvsd.enable_attach()
except:
    print("ptvsd not enabled")

stateStoreName = "statestore"
app=Flask(__name__)

detector = FaceDetection()

dapr_port = int(os.getenv("DAPR_HTTP_PORT", 3500))

def sendToStateStore(img, payload):
    try:
        # how to put images into redis and read back
        # https://localcoder.org/how-to-share-opencv-images-in-two-python-programs

        open_cv_image = numpy.array(img) 
        # Convert RGB to BGR 
        open_cv_image = open_cv_image[:, :, ::-1].copy() 
        h,w = open_cv_image.shape[:2]
        
        detection = detector.detect_single(open_cv_image)
        faceId = None
        gender = None
        if detection is not None:
            faceId = detection.face_id
            gender = detection.face_attributes.gender

        # pack the image
        shape = struct.pack('>II',h,w)
        encoded = shape + open_cv_image.tobytes()
        
        values={'face_id':faceId, 'gender':gender, 'img':bytes.decode(encoded, encoding="ISO-8859-1")}
        with DaprClient() as d:
            # Save state
            print(f"sending FaceId to storage")
            jsonValues = json.dumps(values)
            d.save_state(store_name="statestore", key=str(payload), value=jsonValues)
        return {'faceId':faceId, 'gender':gender}
    except Exception as e:
        logging.error(f"{e}")

@app.route("/", methods=['POST','GET'])
def faceCallApi():
    if request.method == 'GET':
        return "Hello, please use POST\n"
    try:
        imageData = None
        payload=""
        if ('imageData' in request.files):
            imageData = request.files['imageData']
            payload = request.form["id"]
            print (payload)
        else:
            imageData = io.BytesIO(request.get_data())
            print("From get_data")

        img = Image.open(imageData)

        # send to state store
        response = sendToStateStore(img,payload)
        return jsonify(response), 200
    except Exception as e:
        print('EXCEPTION:', str(e))
        return 'Error processing image', 500
        
import signal
import time

class GracefulKiller:
  kill_now = False
  def __init__(self, appToKill):
    self.appToKill = appToKill
    signal.signal(signal.SIGINT, self.exit_gracefully)
    signal.signal(signal.SIGTERM, self.exit_gracefully)

  def exit_gracefully(self, *args):
    self.kill_now = True
    
#killer = GracefulKiller()

#app.run(port=dapr_port)