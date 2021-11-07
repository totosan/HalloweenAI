# import required libraries
import datetime
import multiprocessing
import sys
from mpipe.Pipeline import Pipeline
import numpy as np
import cv2
import mpipe
import coils
import sharedmem

from vidgear.gears import VideoGear
from FaceAPI import FaceDetection

PROCESS_NUM = 2
shared = multiprocessing.Manager().dict()

class gearIt():
    
    def __init__(self, ImageServer) -> None:
            
        # open same stream without stabilization for comparison
        self.stream_org = VideoGear(source="video.mp4").start()
        self.frame = None
        self.detection = FaceDetection()
        # Monitor framerates for the given seconds past.
        self.framerate = coils.RateTicker((1,5,10))
        self.pipe = None
        self.pipe2 = None

        # init http stream
        imageServer = ImageServer(8001, self)
        imageServer.start()

    def get_display_frame(self):
        return shared['out']
        
    def processFrame(self, frame):
        frame = self.detection.detect_faces(frame)
        return frame
    
    def displayFrameOnServer(self, value):
        global forServerFrame
        while True:
            faceFrame = self.pipe.get()
            fps_text = '{:.2f}, {:.2f}, {:.2f} fps'.format(*self.framerate.tick())
            frameBytes = cv2.imencode('.jpg', faceFrame)[1].tobytes()
            shared['out']  = frameBytes

    def run(self):
        # processing frames
        stageProcessFrame = mpipe.OrderedStage(self.processFrame,4)
        #stageReadFrame.link(stageProcessFrame)
        self.pipe = mpipe.Pipeline(stageProcessFrame)
        
        #distributing frames
        stageDisplay = mpipe.OrderedStage(self.displayFrameOnServer)
        self.pipe2 = mpipe.Pipeline(stageDisplay)
        self.pipe2.put(True)
        
        # loop over
        while True:
            # read un-stabilized frame
            frame_org = self.stream_org.read()
            self.pipe.put(frame_org)
        # safely close both video streams
        self.stream_org.stop()
