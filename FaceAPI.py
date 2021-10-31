import asyncio
import io
import glob
import os
import sys
import time
import uuid
import requests
from urllib.parse import urlparse
from io import BytesIO
# To install this module, run:
# python -m pip install Pillow
from PIL import Image, ImageDraw
import cv2
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.face.models import TrainingStatusType, Person

# This key will serve all examples in this document.
KEY = os.getenv("FACE_API_KEY")

# This endpoint will be used in all examples in this quickstart.
ENDPOINT = os.getenv("FACE_API_ENDPOINT")

class FaceDetection():
    def __init__(self) -> None:   
        # Create an authenticated FaceClient.
        self.face_client = FaceClient(ENDPOINT, CognitiveServicesCredentials(KEY))
        self.samplenum = 0
        
    def detect_faces(self, frame):
        # We use detection model 3 to get better performance.
        self.samplenum=self.samplenum+1
        imageName = 'temp.jpg'
        cv2.imwrite(imageName,frame) 
        copyFrame = open(imageName,"r+b")
        detected_faces = self.face_client.face.detect_with_stream(copyFrame, detection_model='detection_03')
        if detected_faces:
           print(' face detected from image')

        # Convert width height to a point in a rectangle
        def getRectangle(faceDictionary):
            rect = faceDictionary.face_rectangle
            left = rect.left
            top = rect.top
            right = left + rect.width
            bottom = top + rect.height
            
            return ((left, top), (right, bottom))

        def drawFaceRectangles(frame) :
            for face in detected_faces:
                start, end = getRectangle(face)
                frame = cv2.rectangle(frame, start,end, (255, 0 , 0), thickness=2)

        # Uncomment this to show the face rectangles.
        drawFaceRectangles(frame)
        return frame