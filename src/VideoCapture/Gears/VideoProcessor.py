# import required libraries
import sys
sys.path.append("./../Tracking/")

import os
import logging
from applicationinsights.logging import LoggingHandler
handler = LoggingHandler(os.getenv('APP_INSIGHTS_KEY',''))
logging.basicConfig(handlers=[ handler ], format='%(levelname)s: %(message)s', level=logging.DEBUG)


import multiprocessing
from multiprocessing.context import Process
import cv2
from Tracking.CentroidItem import CentroidItem
from Tracking.TrackingHelper import TrackingHelper
import coils
from pipe import select, where # https://github.com/JulienPalard/Pipe

from vidgear.gears import VideoGear
from vidgear.gears.asyncio import WebGear
from vidgear.gears.asyncio.helper import reducer

import uvicorn, asyncio, cv2
import aiohttp
import asyncio

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
        self.dapr_url = os.getenv("DAPR_HTTP_URL","http://localhost:{}/").format(self.dapr_port)
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
                try:
                    frame = self.inputQ.get_nowait()
                    # do detection part here
                    detections = self.detector.detect_multi(frame)                
                    objOfInterest = detections
                    if detections.any():
                        self.outputQ.put_nowait(objOfInterest)
                except Exception as e:
                    print(e, flush=True)
                    shared['processStop'] = True
                    logging.error(e)

            
    async def __getObjectDetails__(self, frame, clipregion, id):
        x = int(clipregion[0]-15.0)
        y = int(clipregion[1]-15.0)
        x2 = int(clipregion[2]+15.0)
        y2 = int(clipregion[3]+15.0)

        result = {'gender':None}
        clippedImage = frame[y:y2, x:x2].copy()
        if clippedImage.any():
            cropped = cv2.imencode('.jpg', clippedImage)[1].tobytes()
            try:
                async with aiohttp.ClientSession() as session:
                    data = aiohttp.FormData()
                    data.add_field('imageData', cropped, filename='image.jpg')
                    data.add_field('id',f"{id}")
                    async with session.post(self.dapr_url , data=data, timeout=5, headers = {"dapr-app-id": "faceserver"}) as resp:
                        jsonResponse = await resp.json()
                        logging.info(jsonResponse)
                        if jsonResponse not in [None, {}]:
                            result = jsonResponse

            except Exception as e:
                print("Error sending image to service", flush=True)
                logging.exception("Failed to detect gender")
                
        return result['gender']

    async def addFacesIfExists(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        detectedFacesRects = []
        
        try:
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
                gender = ""
                if trackedIdObj is None and self.dapr_used:
                    print(f"New face detected: {objId}")
                    result = await self.__getObjectDetails__(frame, centroidItem.rect, objId)
                    if result is not None and result != "":
                        gender = result
                        centroidItem.class_type = gender

                trackedIdObj = DetectionHelper.historizeCentroid(trackedIdObj, objId,centroidItem,50)
                self.trackableIDs[objId] = trackedIdObj

                text = f"ID {objId} - {centroidItem.class_type}"
                DetectionHelper.drawCentroid(frame,centroidItem.center,str(len(self.trackableIDs[objId].centroids)))
                DetectionHelper.drawBoundingBoxes(frame,centroidItem.rect, text)
                DetectionHelper.drawMovementArrow(frame,trackedIdObj,centroidItem.center)
        except Exception as e:
            print(e)
            logging.exception('Failed to add faces')
            raise e
        #print(f'No. of trackedFaces: {len(self.trackingManager.correlationTrackers)}')
        return frame       

    async def generateFrames(self):
        global shared
        frameCnt = 0
        while shared['processStop'] == False:
            try:
                # read un-stabilized frame
                frame_org = self.stream_org.read()

                # put as input for face detection
                if frameCnt % FRAME_DIST == 0 and self.inputQ.qsize() < 10:
                    self.inputQ.put_nowait(frame_org)
                    frameCnt = 0 if frameCnt == 100 else frameCnt
                frameCnt = frameCnt + 1

                fps_text = '{:.2f}, {:.2f}, {:.2f} fps'.format(*self.framerate.tick())
                cv2.putText(frame_org, fps_text, (20, 40),cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)

                frame = await self.addFacesIfExists(frame_org)
                
                #print(f'InQ: {self.inputQ.qsize()} OutQ: {self.outputQ.qsize()}')

                # reducer frames size if you want more performance otherwise comment this line
                frame = await reducer(frame, percentage=30)  # reduce frame by 30%
                # handle JPEG encoding
                encodedImage = cv2.imencode(".jpg", frame)[1].tobytes()

                # yield frame in byte format
                yield (b"--frame\r\nContent-Type:video/jpeg2000\r\n\r\n" + encodedImage + b"\r\n")
                await asyncio.sleep(0.00001)  
            except Exception as e:
                logging.error(e, exc_info=True)
                shared['processStop'] = True
                break