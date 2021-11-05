# import required libraries
from vidgear.gears import VideoGear
import numpy as np
import cv2
from threading import Thread
from multiprocessing.pool import ThreadPool
from collections import deque

from FaceAPI import FaceDetection
PROCESS_NUM = 2
class gearIt():
    
    def __init__(self, ImageServer) -> None:
            
        # open same stream without stabilization for comparison
        self.stream_org = VideoGear(source="video.mp4").start()
        self.frame = None
        self.detection = FaceDetection()
        self.pool = ThreadPool(processes=PROCESS_NUM)
        self.pending_task = deque()
        
        # init http stream
        imageServer = ImageServer(8000, self)
        imageServer.start()

    def get_display_frame(self):
        return self.frame

    def processFrame(self,frameNumber, frame):
        if frameNumber % 5 == 0:
            frame = self.detection.detect_faces(frame)
        return frame            

    def run(self):
        # loop over
        frames = 0
        while True:
            
            while len(self.pending_task) > 0 and self.pending_task[0].ready():
                faceFrame = self.pending_task.popleft().get()
                self.frame = cv2.imencode('.jpg', faceFrame)[1].tobytes()
                
            if len(self.pending_task) < PROCESS_NUM:
                # read un-stabilized frame
                frame_org = self.stream_org.read()
                if not frame_org is None:
                    frames = frames +1
                    if frames % 5 == 0:
                        t = self.pool.apply_async(self.processFrame, (frames,frame_org.copy()))
                        self.pending_task.append(t)
                    else:
                        self.frame = cv2.imencode('.jpg', frame_org)[1].tobytes()
                    
                    print(frames)
            

        # safely close both video streams
        self.stream_org.stop()

