# import required libraries
from logging import currentframe
import multiprocessing
from multiprocessing import queues
import os
from time import sleep, time, perf_counter
from azure.cognitiveservices.vision import face
import cv2
import mpipe
import coils

from vidgear.gears import VideoGear
from FaceAPI import FaceDetection

# debugger exception with EOFError <-- reason: bug in debugger on multiprocessing

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
        self.imageProcessingPipe = None
        self.renderingPipe = None


        # init http stream
        imageServer = ImageServer(8001, self)
        imageServer.start()

    # Convert width height to a point in a rectangle
    @staticmethod
    def getRectangle(faceDictionary):
        rect = faceDictionary.face_rectangle
        left = rect.left
        top = rect.top
        right = left + rect.width
        bottom = top + rect.height
        
        return ((left, top), (right, bottom))
    
    @staticmethod
    def drawFaceRectangles(frame, detected_faces) :
        for face in detected_faces:
            start, end = gearIt.getRectangle(face)
            frame = cv2.rectangle(frame, start,end, (255, 0 , 0), thickness=2)

    def get_display_frame(self):
        faces = shared['out']
        currentFrame = shared['current']
        if faces:
            gearIt.drawFaceRectangles(currentFrame, faces)
        frameBytes = cv2.imencode('.jpg',currentFrame)[1].tobytes()
        return frameBytes
        
    def processFrame(self, frame):
        print(f'ProcessID process: {os.getpid()}')
        #sleep(0.6)
        faces = None
        faces = self.detection.detect_faces(frame)
        return faces
    
    def displayFrameOnServer(self, value):
        global forServerFrame
        
        while True:
            print(f'ProcessID grab: {os.getpid()}')
            faces = self.imageProcessingPipe.get()
            fps_text = '{:.2f}, {:.2f}, {:.2f} fps'.format(*self.framerate.tick())
            print(fps_text, len(faces))
            shared['out']  = faces

    def generateFrames(self,value):
        while True:
            print(f'ProcessID generate: {os.getpid()}')
        
            tic = perf_counter()
            # read un-stabilized frame
            frame_org = self.stream_org.read()
            self.imageProcessingPipe.put(frame_org)
            toc = perf_counter()
            print(f'Time to put into processing pipe {toc-tic:0.4f}s')
            shared['current'] = frame_org

    def run(self):
        # processing frames
        stageProcessFrame =  mpipe.OrderedStage(self.processFrame)
        #stageProcessFrame = mpipe.FilterStage(( mpipe.UnorderedStage(self.processFrame),),max_tasks=4)
        self.imageProcessingPipe = mpipe.Pipeline(stageProcessFrame)
                
        #distributing frames
        stageDisplay = mpipe.UnorderedStage(self.displayFrameOnServer)
        self.renderingPipe = mpipe.Pipeline(stageDisplay)
        self.renderingPipe.put(True)
    
        stageGenerate = mpipe.UnorderedStage(self.generateFrames)
        pipe = mpipe.Pipeline(stageGenerate)
        pipe.put(True)
        
        try: 
            while True:
                sleep(0.01)

            if False:
                # loop over
                while True:
                    print(f'ProcessID Main: {os.getpid()}')
                    
                    # read un-stabilized frame
                    frame_org = self.stream_org.read()
                    self.imageProcessingPipe.put(frame_org)
                    shared['current'] = frame_org
                
        except KeyboardInterrupt as e :
            print(e)
        finally:
            print("Stoppig pipeline")
            # safely close both video streams
            self.imageProcessingPipe.put(None)
            #self.renderingPipe.put(None)
            self.stream_org.stop()