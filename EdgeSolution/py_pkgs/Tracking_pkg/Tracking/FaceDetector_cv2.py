import cv2
import imutils
import numpy as np
from Tracking.DetectionBase import DetectionBase
from Tracking.CentroidItem import CentroidItem

CONFIDENCE = 0.3
import pkg_resources

DATA_PATH = pkg_resources.resource_filename('Tracking', 'dnn/face_detector/')

class FaceDetectorDnn(DetectionBase):
    def __init__(self) -> None:
        super().__init__()
        prototxt = f"{DATA_PATH}/deploy.prototxt"
        weights = f"{DATA_PATH}/res10_300x300_ssd_iter_140000.caffemodel"
        self.net = cv2.dnn.readNetFromCaffe(prototxt, weights)

    def detect_multi(self, frame):
        frame = imutils.resize(frame, width=400)
        
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0,(300, 300), (104.0, 117.0, 123.0))
        self.net.setInput(blob)
        detections = self.net.forward()
        return detections

    def detect_single(self, frame):
        return super().detect_single(frame)
