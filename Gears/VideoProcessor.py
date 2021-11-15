# import required libraries
from logging import currentframe
import multiprocessing
from multiprocessing.context import Process
import os
from time import sleep
import cv2
import coils
from vidgear.gears import VideoGear
from azure.cognitiveservices.vision import face
from Tracking.centroidtracker import CentroidTracker

# debugger exception with EOFError <-- reason: bug in debugger on multiprocessing

PROCESS_NUM = 2
shared = multiprocessing.Manager().dict()
processMem = multiprocessing.Manager().Value('b',False)

class VideoProcessor():

    def __init__(self, ImageServer, Detector) -> None:

        # open same stream without stabilization for comparison
        self.stream_org = VideoGear(source="video.mp4").start()
        self.detection = Detector
        self.tracker = CentroidTracker()
        prototxt = "./Tracking/dnn/face_detector/deploy.prototxt"
        weights = "./Tracking/dnn/face_detector/weights.meta4"
        net = cv2.dnn.readNetFromCaffe(prototxt, weights)
        
        # Monitor framerates for the given seconds past.
        self.framerate = coils.RateTicker((1, 5, 10))
        self.frame = None

        self.inputQ = multiprocessing.Queue()
        self.outputQ = multiprocessing.Queue()
        
        # init http stream
        imageServer = ImageServer(8001, self)
        imageServer.start()

    def get_display_frame(self):
        global shared
        global processMem
        faces = None
        try:
            if processMem.value == False:
                faces = shared['out']
                currentFrame = shared['current']
                if faces:
                    VideoProcessor.drawFaceRectangles(currentFrame, faces)
                frameBytes = cv2.imencode('.jpg', currentFrame)[1].tobytes()
                return frameBytes
        except Exception as e:
            print("Exception on serving frames")

    def processFrame(self):
        global processMem
        while processMem.value == False:
            if not self.inputQ.empty() is True:
                frame = self.inputQ.get_nowait()
                print(f'ProcessID process: {os.getpid()}')
                objOfInterest = None
                self.outputQ.put_nowait(objOfInterest)

    def displayFrameOnServer(self):
        global shared
        global processMem
        while processMem.value == False:
            if not self.outputQ.empty() is True:
                faces = self.outputQ.get_nowait()
                print(f'ProcessID grab: {os.getpid()}')
                shared['out'] = faces

    def generateFrames(self):
        global shared
        frameCnt = 0
        while True:
            # read un-stabilized frame
            frame_org = self.stream_org.read()

            # put as input for face detection
            if frameCnt % 1 == 0 :
                self.inputQ.put_nowait(frame_org)
                frameCnt = 0
            frameCnt = frameCnt + 1

            fps_text = '{:.2f}, {:.2f}, {:.2f} fps'.format(*self.framerate.tick())
            print(fps_text)
            fps_current = self.framerate.tick()[0]
            wait_time = 0.001
            if fps_current>26.0:
                wait_time=1/(fps_current-25.0)
            
            sleep(wait_time)
            # make current frame for anything available in shared memory
            shared['current'] = frame_org

    def run(self):
        # run processes for video processing        
        processesProcessing = [Process(target=self.processFrame,daemon=True) for _ in range(5)]
        for p in processesProcessing:
            p.start()
            
        procRender = Process(target=self.displayFrameOnServer, daemon=True)
        procRender.start()
        
        try:
            self.generateFrames()

        except KeyboardInterrupt as e:
            print("STRG+C pressed")
            processMem.set(True)
            procRender.terminate()
            for p in processesProcessing:
                p.terminate()
        finally:
            print("Stoppig pipeline")
            self.stream_org.stop()
