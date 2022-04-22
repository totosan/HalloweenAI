from Tracking.gfx.DetectionHelper import DetectionHelper
import dlib 

class TrackingHelper:
    def __init__(self) -> None:
        self.correlationTrackers = []
            
    def createTrackers(self, detections, frameRGB) -> None:
        self.correlationTrackers.clear()
        for i,faceRect in enumerate(detections):
            (startX, startY, endX, endY) = faceRect.astype("int")
            detections[i] =[int(coord) for coord in faceRect]
            dlibCorrelationTracker = dlib.correlation_tracker()
            correlationRect = dlib.rectangle(startX, startY, endX, endY)
            dlibCorrelationTracker.start_track(frameRGB,correlationRect)
            
            self.correlationTrackers.append(dlibCorrelationTracker)
        

    def updateTrackers(self,frameRGB):
        detections = []
        for tracker in self.correlationTrackers:
            psr = tracker.update(frameRGB)
            pos = tracker.get_position()
            # unpack the position object
            startX = int(pos.left())
            startY = int(pos.top())
            endX = int(pos.right())
            endY = int(pos.bottom())

            detections.append((startX, startY, endX, endY))
        return detections
                