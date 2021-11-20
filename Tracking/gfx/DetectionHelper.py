import numpy as np
import dlib
import cv2
import pipe

from Tracking.trackableobject import TrackableObject

class DetectionHelper():
    @staticmethod
    def getBoundingBoxesFromDetections(detections, frame, confidenceThreshold=0.5):
        (h, w) = frame.shape[:2]
        rects = []
        for i in range(0, detections.shape[2]):
            # extract the confidence (i.e., probability) associated with the
            # prediction
            confidence = detections[0, 0, i, 2]
            # filter out weak detections by ensuring the `confidence` is
            # greater than the minimum confidence
            if confidence < confidenceThreshold:
                continue
            # compute the (x, y)-coordinates of the bounding box for the
            # object
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            rects.append(box)
        return rects

    @staticmethod
    def createTrackers(detections, frameRGB):
        trackers=[]
        for i,faceRect in enumerate(detections):
            (startX, startY, endX, endY) = faceRect.astype("int")
            detections[i] =[int(coord) for coord in faceRect]
            dlibCorrelationTracker = dlib.correlation_tracker()
            correlationRect = dlib.rectangle(startX, startY, endX, endY)
            dlibCorrelationTracker.start_track(frameRGB,correlationRect)
            trackers.append(dlibCorrelationTracker)
        return trackers

    @staticmethod
    def updateTrackers(trackers, frameRGB):
        detections = []
        for tracker in trackers:
            tracker.update(frameRGB)
            pos = tracker.get_position()
            # unpack the position object
            startX = int(pos.left())
            startY = int(pos.top())
            endX = int(pos.right())
            endY = int(pos.bottom())

            detections.append((startX, startY, endX, endY))
        return detections
    
    @staticmethod
    def drawBoundingBoxes(frame, box, text=None):
        (startX, startY, endX, endY) = box
        y = startY - 10 if startY - 10 > 10 else startY + 10
        cv2.rectangle(frame, (startX, startY), (endX, endY),(0, 0, 255), 2)
        if text:
            cv2.putText(frame, text, (startX, y),cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
    
    @staticmethod
    def drawCentroid(frame, centerPoint, text=None):
        (centroidX, centroidY) = centerPoint
        cv2.circle(frame, (centroidX, centroidY), 4, (0, 255, 0), -1)
        if text:
            cv2.putText(frame, text, (centroidX - 10, centroidY - 10),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    @staticmethod
    def historizeCentroid(id_to_track, objId, centroidObject, historyLimit=0):
        if id_to_track == None:
            id_to_track = TrackableObject(objId,0,centroidObject)
        else:
            id_to_track.centroids.append(centroidObject)
        if historyLimit > 0 and len(id_to_track.centroids) >= historyLimit:
            id_to_track.centroids = id_to_track.centroids[:-39]

        return id_to_track
    
    @staticmethod
    def drawMovementArrow(frame, trackedObj, currentCentroid):
        y = [c.center[1] for c in trackedObj.centroids]
        x = [c.center[0] for c in trackedObj.centroids]
        (centerX, centerY) = currentCentroid

        directionY = centerY - np.mean(y)
        directionX = centerX - np.mean(x)
        directX = int(round(directionX,1))
        directY = int(round(directionY,1))
        
        colorArrow = (0,0,250)
        
        cv2.arrowedLine(frame, 
            (centerX, centerY), (centerX+directX, centerY+directY), 
            colorArrow, 2)
