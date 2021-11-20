import multiprocessing
from multiprocessing.context import Process
from os import stat
from Tracking.gfx.DetectionHelper import DetectionHelper
from multiprocessing import Queue
import dlib 

class TrackingHelper:
    def __init__(self) -> None:
        self.inputQueues= []
        self.outputQueues= []
    
    def startTrackerProcess(self, box, lable, rgb) -> Process:
        inQ = Queue()
        outQ = Queue()
        self.inputQueues.append(inQ)
        self.outputQueues.append(outQ)
        
        p = multiprocessing.Process(target= self._trackingProcess, args=(box, lable,rgb,inQ, outQ))
        p.daemon = True
        p.start()
        return p
        
    def createTrackers(self, detections, frameRGB):
        trackers=[]        
        for i,faceRect in enumerate(detections):
            (startX, startY, endX, endY) = faceRect.astype("int")
            detections[i] =[int(coord) for coord in faceRect]
            dlibCorrelationTracker = dlib.correlation_tracker()
            correlationRect = dlib.rectangle(startX, startY, endX, endY)
            dlibCorrelationTracker.start_track(frameRGB,correlationRect)
            trackers.append(dlibCorrelationTracker)
        return trackers

    def updateTrackers(self, trackers, frameRGB):
        detections = []
        for tracker in trackers:
            psr = tracker.update(frameRGB)
            pos = tracker.get_position()
            # unpack the position object
            startX = int(pos.left())
            startY = int(pos.top())
            endX = int(pos.right())
            endY = int(pos.bottom())

            detections.append((startX, startY, endX, endY))
        return detections
    
    def _trackingProcess(self,box, lable, rgb, inQ, outQ):
        trackers = self.createTrackers((box),rgb)
        while True:
        
            rgb = inQ.get()
            if not rgb is None:
                regions = self.updateTrackers(trackers,rgb)
                if len(regions)==1:
                    outQ.put((lable,regions[0][0]))
                