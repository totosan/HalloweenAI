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
        print(f'Video source is {video_source}')
        streamMode = True if "youtu" in video_source else False

        # various performance tweaks
        self.options = {
            "custom_data_location":"./",
            #"frame_size_reduction": 25,
            "enable_live_braodcast":True,
        }   
        # open same stream without stabilization for comparison
        self.stream_org = VideoGear(source=video_source, stream_mode=streamMode, framerate=30).start()
        self.web_stream = WebGear(logging=True, **self.options)

        # add your custom frame producer to config
        self.web_stream.config["generator"] = self.generateFrames

        self.detection = DetectionBase()
        self.detection = Detector
        self.tracker = CentroidTracker()
        
        # Monitor framerates for the given seconds past.
        self.framerate = coils.RateTicker((1, 5, 10))
        self.frame = None

        self.inputQ = multiprocessing.Queue()
        self.outputQ = multiprocessing.Queue()
        shared['processStop'] = False

    def processFrame(self):
        global processMem
        while shared['processStop'] == False:
            if not self.inputQ.empty() is True:
                frame = self.inputQ.get_nowait()
                detections = self.detection.detect_multi(frame)
                objOfInterest = detections
                self.outputQ.put_nowait(objOfInterest)

    async def displayFrameOnServer(self, frame):
        if not self.outputQ.empty() is True:
            faces = self.outputQ.get_nowait()
            if faces.any():
                frame = self.detection.render(faces,frame)               
        return frame              

    async def generateFrames(self):
        global shared
        frameCnt = 0
        while shared['processStop'] == False:
            # read un-stabilized frame
            frame_org = self.stream_org.read()

            # put as input for face detection
            if frameCnt % 5 == 0 :
                self.inputQ.put_nowait(frame_org)
                frameCnt = 0
            frameCnt = frameCnt + 1

            fps_text = '{:.2f}, {:.2f}, {:.2f} fps'.format(*self.framerate.tick())
            cv2.putText(frame_org, fps_text, (20, 40),cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)

            frame = await self.displayFrameOnServer(frame_org)
            # reducer frames size if you want more performance otherwise comment this line
            frame = await reducer(frame, percentage=30)  # reduce frame by 30%
            # handle JPEG encoding
            encodedImage = cv2.imencode(".jpg", frame)[1].tobytes()

            # yield frame in byte format
            yield (b"--frame\r\nContent-Type:video/jpeg2000\r\n\r\n" + encodedImage + b"\r\n")
            await asyncio.sleep(0.00001)  

    def run(self):
        # run processes for video processing        
        processesProcessing = [Process(target=self.processFrame,daemon=True) for _ in range(1)]
        for p in processesProcessing:
            p.start()
        
        # run this app on Uvicorn server at address http://localhost:8000/
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