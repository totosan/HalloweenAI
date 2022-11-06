import sys


import base64
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
import cv2
import numpy
from Tracking.FaceAPI import FaceDetection

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
 
try:
    import ptvsd
    ptvsd.enable_attach()
except:
    print("ptvsd not enabled")

stateStoreName = "statestore"
app=Flask(__name__)

detector = FaceDetection()

dapr_port = int(os.getenv("DAPR_HTTP_PORT", 3000))
use_faceapi = os.getenv("FACEAPI_USED",False)

def sendToStateStore(img, payload):
    try:
        # how to put images into redis and read back
        # https://localcoder.org/how-to-share-opencv-images-in-two-python-programs

        open_cv_image = numpy.array(img) 
        # Convert RGB to BGR 
        open_cv_image = open_cv_image[:, :, ::-1].copy() 
        faceId = str(payload)
        gender = ""
        
        if use_faceapi:
            detection = detector.detect_single(open_cv_image)
            if detection is not None:
                faceId = detection.face_id
                gender = detection.face_attributes.gender

        # pack the image
        ret, imgJpg = cv2.imencode('.jpg', open_cv_image)
        b64Image = base64.b64encode(imgJpg)
 
        values={'face_id':faceId, 'gender':gender, 'img':bytes.decode(b64Image, encoding='ISO-8859-1')}
        if True:
            with DaprClient() as d:
                # Save state
                logging.info(f"sending FaceId to storage")
                jsonValues = json.dumps(values)
                d.save_state(store_name="statestore", key=str(payload), value=jsonValues)
        return {'faceId':faceId, 'gender':gender}
    except Exception as e:
        logging.exception(e)

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
        elif ('imageData' in request.form):
            imageData = request.form['imageData']
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