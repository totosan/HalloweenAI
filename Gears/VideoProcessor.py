# import required libraries
from logging import currentframe
import multiprocessing
from multiprocessing.context import Process
import os
from time import sleep
from azure.cognitiveservices.vision import face
import cv2
import coils
from vidgear.gears import VideoGear
from vidgear.gears.asyncio import WebGear
from vidgear.gears.asyncio.helper import reducer
from starlette.responses import StreamingResponse
from starlette.routing import Route

import uvicorn, asyncio, cv2

from Tracking.DetectionBase import DetectionBase
from Tracking.centroidtracker import CentroidTracker

# debugger exception with EOFError <-- reason: bug in debugger on multiprocessing

PROCESS_NUM = 2
shared = multiprocessing.Manager().dict()

class VideoProcessor():
    
    def __init__(self, ImageServer, Detector) -> None:
        video_source = os.getenv("VIDEO_PATH","video.mp4")
        streamMode = True if "youtu" in video_source else False

        # various performance tweaks
        self.options = {
            "custom_data_location":"./",
            "frame_size_reduction": 50,
            "enable_live_braodcast":True,
        }   
        # open same stream without stabilization for comparison
        print("**************************")
        print(f'* Video: {video_source}')
        print(f'* Streaming: {streamMode}')
        print(f'* Config: {self.options}')
        print("**************************")

        self.stream_org = VideoGear(source=video_source, stream_mode=streamMode, framerate=30).start()
        self.web_stream = WebGear(logging=True, **self.options)

        # add your custom frame producer to config
        self.web_stream.config["generator"] = self.generateFrames

        self.detection = DetectionBase()
        self.detection = Detector
        self.tracker = CentroidTracker(maxDisappeared=10, maxDistance=20)
        
        # Monitor framerates for the given seconds past.
        self.framerate = coils.RateTicker((1, 5, 10))
        self.frame = None

        self.inputQ = multiprocessing.Queue()
        self.outputQ = multiprocessing.Queue()
        shared['processStop'] = False

    def run(self):
        # run processes for video processing        
        processesProcessing = [Process(target=self.processFrame,daemon=True) for _ in range(2)]
        for p in processesProcessing:
            p.start()
        
        uvicorn.run(self.web_stream(), host="0.0.0.0", port=8081)

        # close app safely
        self.web_stream.shutdown()
        
        print("Stopping processes")
        shared['processStop'] = True
        self.stream_org.stop()
        self.inputQ.close()
        self.outputQ.close()
        # terminating all processes
        for p in processesProcessing:
            p.terminate()

            
    def processFrame(self):
        global shared
        while shared['processStop'] == False:
            if not self.inputQ.empty() is True:
                frame = self.inputQ.get_nowait()
                
                # do detection part here
                detections = self.detection.detect_multi(frame)                
                objOfInterest = detections
                self.outputQ.put_nowait(objOfInterest)

    def addFacesIfExists(self, frame):
        if not self.outputQ.empty() is True:
            faces = self.outputQ.get_nowait()

            if faces.any():
                detectionsRects = []
                frame, detectionsRects = self.detection.render(faces,frame)
                
                objects = self.tracker.update(detectionsRects)
                for (objId, centroidObject) in objects.items():
                    text = "ID {}".format(objId)
                    centroid = centroidObject.center
                    className = centroidObject.class_type
                    faceRect = centroidObject.rect

                    cv2.putText(frame, text, (centroid[0] - 10, centroid[1] - 10),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    cv2.circle(frame, (centroid[0], centroid[1]), 4, (10*objId, 255, 0), -1)
 
        
        return frame       

    async def generateFrames(self):
        global shared
        frameCnt = 0
        while shared['processStop'] == False:
            # read un-stabilized frame
            frame_org = self.stream_org.read()

            # put as input for face detection
            if frameCnt % 7 == 0 and self.inputQ.qsize() < 10:
                self.inputQ.put_nowait(frame_org)
                frameCnt = 0
            frameCnt = frameCnt + 1

            fps_text = '{:.2f}, {:.2f}, {:.2f} fps'.format(*self.framerate.tick())
            cv2.putText(frame_org, fps_text, (20, 40),cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)

            frame = self.addFacesIfExists(frame_org)
            
            print(f'InQ: {self.inputQ.qsize()}')
            print(f'OutQ: {self.outputQ.qsize()}')

            # reducer frames size if you want more performance otherwise comment this line
            frame = await reducer(frame, percentage=30)  # reduce frame by 30%
            # handle JPEG encoding
            encodedImage = cv2.imencode(".jpg", frame)[1].tobytes()

            # yield frame in byte format
            yield (b"--frame\r\nContent-Type:video/jpeg2000\r\n\r\n" + encodedImage + b"\r\n")
            await asyncio.sleep(0.00001)  
