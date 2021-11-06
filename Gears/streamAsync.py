# import required libraries
import datetime
import sys
import numpy as np
import cv2
import mpipe
import coils

from vidgear.gears import VideoGear
from FaceAPI import FaceDetection

PROCESS_NUM = 2

class gearIt():
    
    def __init__(self, ImageServer) -> None:
            
        # open same stream without stabilization for comparison
        self.stream_org = VideoGear(source="video.mp4").start()
        self.frame = None
        self.detection = FaceDetection()
        # Monitor framerates for the given seconds past.
        self.framerate = coils.RateTicker((1,5,10))

        # init http stream
        imageServer = ImageServer(8000, self)
        imageServer.start()

    def get_display_frame(self):
        return self.frame

    def processFrame(self, frame):
        frame = self.detection.detect_faces(frame)
        return frame
    
    def processFrameDummy(self, frame):
        return (frame,2)
    
    def displayFrameOnServer(self,faceFrame):
        fps_text = '{:.2f}, {:.2f}, {:.2f} fps'.format(*self.framerate.tick())
        self.frame = cv2.imencode('.jpg', faceFrame)[1].tobytes()
        
    def run(self):
        stage1 = mpipe.OrderedStage(self.processFrameDummy)
        stage2 = mpipe.OrderedStage(self.displayFrameOnServer)
        stage1.link(stage2)
        pipe = mpipe.Pipeline(stage1)
        
        # loop over
        while True:
            # read un-stabilized frame
            frame_org = self.stream_org.read()
            pipe.put(frame_org)
        # safely close both video streams
        self.stream_org.stop()
