import cv2
import imutils
import numpy as np
from Tracking.DetectionBase import DetectionBase
from Tracking.CentroidItem import CentroidItem

CONFIDENCE = 0.3

class FaceDetectorDnn(DetectionBase):
    def __init__(self) -> None:
        super().__init__()
        prototxt = "./Tracking/dnn/face_detector/deploy.prototxt"
        weights = "./Tracking/dnn/face_detector/res10_300x300_ssd_iter_140000.caffemodel"
        self.net = cv2.dnn.readNetFromCaffe(prototxt, weights)

    def detect_multi(self, frame):
        frame = imutils.resize(frame, width=400)
        
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0,(300, 300), (104.0, 117.0, 123.0))
        self.net.setInput(blob)
        detections = self.net.forward()
        return detections

    def detect_single(self, frame):
        return super().detect_single(frame)

    def render(self, detections, frame):
        (h, w) = frame.shape[:2]
        rects = []
        for i in range(0, detections.shape[2]):
            # extract the confidence (i.e., probability) associated with the
            # prediction
            confidence = detections[0, 0, i, 2]
            # filter out weak detections by ensuring the `confidence` is
            # greater than the minimum confidence
            if confidence < CONFIDENCE:
                continue
            # compute the (x, y)-coordinates of the bounding box for the
            # object
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            item = CentroidItem(0,None,box.astype("int"))
            rects.append(box)
            (startX, startY, endX, endY) = box.astype("int")
    
            # draw the bounding box of the face along with the associated
            # probability
            text = "{:.2f}%".format(confidence * 100)
            y = startY - 10 if startY - 10 > 10 else startY + 10
            cv2.rectangle(frame, (startX, startY), (endX, endY),(0, 0, 255), 2)
            cv2.putText(frame, text, (startX, y),cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
        return frame, rects