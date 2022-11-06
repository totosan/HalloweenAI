import os
import cv2
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials

from Tracking.DetectionBase import DetectionBase

# This key will serve all examples in this document.
KEY = os.getenv("FACE_API_KEY")

# This endpoint will be used in all examples in this quickstart.
ENDPOINT = os.getenv("FACE_API_ENDPOINT")

class FaceDetection(DetectionBase):
    def __init__(self) -> None:   
        # Create an authenticated FaceClient.
        self.face_client = FaceClient(ENDPOINT, CognitiveServicesCredentials(KEY))
        self.samplenum = 0

        
    def detect_multi(self, frame):
        # We use detection model 3 to get better performance.
        self.samplenum=self.samplenum+1
        imageName = 'temp.jpg'
        cv2.imwrite(imageName,frame) 
        copyFrame = open(imageName,"r+b")
        try:
            detected_faces = self.face_client.face.detect_with_stream( copyFrame, detection_model='detection_03', recognition_model='recognition_04', return_face_attributes=['age','gender'])
        except Exception as e:
            print(e)
            detected_faces = None
            
            
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

        if detected_faces:
            print(f' faces detected from image: {len(detected_faces)}')
            # Uncomment this to show the face rectangles.
            # drawFaceRectangles(frame)
            
        return detected_faces
    
    def detect_single(self, frame):
        # We use detection model 3 to get better performance.
        self.samplenum=self.samplenum+1
        imageName = 'temp.jpg'
        cv2.imwrite(imageName,frame) 
        copyFrame = open(imageName,"r+b")
        try:
            detected_faces = self.face_client.face.detect_with_stream( copyFrame, detection_model='detection_01', recognition_model='recognition_04', return_face_attributes=['age','gender'])
        except Exception as e:
            print(e)
            detected_faces = None
            
            
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

        returnValue=None
        if detected_faces is not None and len(detected_faces)>0:
            if len(detected_faces)>1:
                print('Expected one face, but got {}.'.format(len(detected_faces)))
            returnValue = detected_faces[0]
        return returnValue


