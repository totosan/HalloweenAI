# import required libraries
from logging import currentframe
import multiprocessing
from multiprocessing.context import Process
from multiprocessing.queues import Queue
import os
from time import sleep
import cv2
from numpy import string_
from Tracking.CentroidItem import CentroidItem
from Tracking.FaceDetector_cv2 import CONFIDENCE
from Tracking.TrackingHelper import TrackingHelper
from Tracking.TrackingHelper_multi import TrackingHelper_multi
from Tracking.trackableobject import TrackableObject
import dlib
import coils
from pipe import select, where # https://github.com/JulienPalard/Pipe

from vidgear.gears import VideoGear
from vidgear.gears.asyncio import WebGear
from vidgear.gears.asyncio.helper import reducer
from starlette.responses import StreamingResponse
from starlette.routing import Route

import uvicorn, asyncio, cv2
import requests

from Tracking.DetectionBase import DetectionBase
from Tracking.centroidtracker import CentroidTracker
from Tracking.gfx.DetectionHelper import DetectionHelper

# debugger exception with EOFError <-- reason: bug in debugger on multiprocessing

DETECTOR_PROCESS_NUM = 1
CONFIDENCE = 0.3
FRAME_DIST = 5
shared = multiprocessing.Manager().dict()

class VideoProcessor():
    
    def __init__(self, Detector) -> None:
        video_source = os.getenv("VIDEO_PATH","video.mp4")
        streamMode = True if "youtu" in video_source else False
        self.dapr_port = os.getenv("DAPR_HTTP_PORT", 3500)
        self.dapr_url = "http://localhost:{}/".format(self.dapr_port)
        self.dapr_used = os.getenv("DAPR_USED", False)

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

        self.stream_org = VideoGear(source=video_source, stream_mode=streamMode, framerate=25).start()
        self.web_stream = WebGear(logging=True, **self.options)

        # add your custom frame producer to config
        self.web_stream.config["generator"] = self.generateFrames

        self.detector = DetectionBase()
        self.detector = Detector
        self.centroids = CentroidTracker(maxDisappeared=10, maxDistance=50)
        
        self.trackableIDs = {}
        self.trackingManager = TrackingHelper()

        # Monitor framerates for the given seconds past.
        self.framerate = coils.RateTicker((1, 5, 10))
        self.frame = None

        self.frameInQueues = []
        self.frameOutQueues = []

        self.inputQ = multiprocessing.Queue()
        self.outputQ = multiprocessing.Queue()
        shared['processStop'] = False

    def run(self):
        # run processes for video processing        
        processesProcessing = [Process(target=self.processFrame,daemon=True) for _ in range(DETECTOR_PROCESS_NUM)]
        for p in processesProcessing:
            p.start()
        
        uvicorn.run(self.web_stream(), host="0.0.0.0", port=8080)

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
        self.correlationTrackers = []
        while shared['processStop'] == False:
            if not self.inputQ.empty() is True:
                frame = self.inputQ.get_nowait()
                # do detection part here
                detections = self.detector.detect_multi(frame)                
                objOfInterest = detections
                if detections.any():
                    self.outputQ.put_nowait(objOfInterest)

    def sendToFacesStore(self, id):
        message = {"id":f"{id}"}
        print(f"sending FaceId to service: {self.dapr_url}")
        try:
            response = requests.post(self.dapr_url, json=message, timeout=5, headers = {"dapr-app-id": "faceserver"} )
            if not response.ok:
                print("HTTP %d => %s" % (response.status_code,
                                        response.content.decode("utf-8")), flush=True)
        except Exception as e:
            print(e, flush=True)

    def addFacesIfExists(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        detectedFacesRects = []
        
        # create or update face tracker 
        if not self.outputQ.empty() is True:
            faces = self.outputQ.get_nowait()
            detectedFacesRects = DetectionHelper.getBoundingBoxesFromDetections(faces,frame)
            detectedFacesRects = [val.astype("int") for val in detectedFacesRects] # move to centroidItem.rect
            self.trackingManager.createTrackers(detectedFacesRects,rgb)
        else :
            detectedFacesRects = self.trackingManager.updateTrackers(rgb)

        # add IDs to tracked regions
        centroidItems = list(detectedFacesRects | select(lambda x:CentroidItem(class_type=0, rect=x)))
        trackedCentroidItems = self.centroids.update(centroidItems)

        for (objId, centroidItem) in trackedCentroidItems.items():
            trackedIdObj = self.trackableIDs.get(objId,None)
            if trackedIdObj is None and self.dapr_used:
                print(f"New face detected: {objId}")
                self.sendToFacesStore(objId)
            trackedIdObj = DetectionHelper.historizeCentroid(trackedIdObj, objId,centroidItem,50)
            self.trackableIDs[objId] = trackedIdObj

            text = "ID {}".format(objId)
            DetectionHelper.drawCentroid(frame,centroidItem.center,str(len(self.trackableIDs[objId].centroids)))
            DetectionHelper.drawBoundingBoxes(frame,centroidItem.rect, text)
            DetectionHelper.drawMovementArrow(frame,trackedIdObj,centroidItem.center)

        print(f'No. of trackedFaces: {len(self.trackingManager.correlationTrackers)}')
        return frame       

    async def generateFrames(self):
        global shared
        frameCnt = 0
        while shared['processStop'] == False:
            # read un-stabilized frame
            frame_org = self.stream_org.read()

            # put as input for face detection
            if frameCnt % FRAME_DIST == 0 and self.inputQ.qsize() < 10:
                self.inputQ.put_nowait(frame_org)
                frameCnt = 0 if frameCnt == 100 else frameCnt
            frameCnt = frameCnt + 1

            fps_text = '{:.2f}, {:.2f}, {:.2f} fps'.format(*self.framerate.tick())
            cv2.putText(frame_org, fps_text, (20, 40),cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)

            frame = self.addFacesIfExists(frame_org)
            
            print(f'InQ: {self.inputQ.qsize()} OutQ: {self.outputQ.qsize()}')

            # reducer frames size if you want more performance otherwise comment this line
            frame = await reducer(frame, percentage=30)  # reduce frame by 30%
            # handle JPEG encoding
            encodedImage = cv2.imencode(".jpg", frame)[1].tobytes()

            # yield frame in byte format
            yield (b"--frame\r\nContent-Type:video/jpeg2000\r\n\r\n" + encodedImage + b"\r\n")
            await asyncio.sleep(0.00001)  
