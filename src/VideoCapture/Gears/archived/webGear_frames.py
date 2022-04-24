# import required libraries
import os
import uvicorn
# import necessary libs
import uvicorn, asyncio, cv2
import utils
import mpipe
import coils

#from vidgear.gears.asyncio import WebGear_RTC
from vidgear.gears.asyncio import WebGear
from vidgear.gears.asyncio.helper import reducer
from starlette.responses import StreamingResponse
from starlette.routing import Route
from Tracking.FaceAPI import FaceDetection

class gearIt(object):
    def __init__(self, *args):
        self.youtube = os.getenv("VIDEO_PATH")
        self.stream = os.getenv("STREAM_URI",self.youtube)
        self.video = "video.mp4"
        
        print("****************************")
        print(f'* VIDEO_PATH: {self.youtube}')
        print(f'* STREAM_URI: {self.stream}')
        print("****************************")
        # various performance tweaks
        self.options = {
            "custom_data_location":"./",
            "frame_size_reduction": 25,
            "enable_live_braodcast":True,
        }   
        # Monitor framerates for the given seconds past.
        self.framerate = coils.RateTicker((1,5,10))
        
        self.detection = FaceDetection()

    def run(self):
        # initialize WebGear_RTC app
        web = WebGear(logging=True, **self.options)

        # add your custom frame producer to config
        web.config["generator"] = self.my_frame_producer1
        
        # run this app on Uvicorn server at address http://localhost:8000/
        uvicorn.run(web(), host="0.0.0.0", port=8081)

        # close app safely
        web.shutdown()
        
    def processFrame(self, frame):
        frame = self.detection.detect_faces(frame)

    
    def display(self,frame):
        fps='{:.2f}, {:.2f}, {:.2f} fps'.format(*self.framerate.tick())
        utils.writeOSD(
            frame,
            ('FPS',fps),
        )
        return frame
    
    # create your own custom frame producer
    async def my_frame_producer1(self):
        stage1 = mpipe.OrderedStage(self.processFrame)
        stage2 = mpipe.OrderedStage(self.display)
        stage1.link(stage2)
        pipe = mpipe.Pipeline(stage1)
        
        # !!! define your first video source here !!!
        # Open any video stream such as "foo1.mp4"
        stream = cv2.VideoCapture(self.video)
        # loop over frames
        while True:
            for result in pipe.results():
                # handle JPEG encoding
                encodedImage = cv2.imencode(".jpg", result)[1].tobytes()
                # yield frame in byte format
                yield (b"--frame\r\nContent-Type:video/jpeg2000\r\n\r\n" + encodedImage + b"\r\n")
                
            # read frame from provided source
            (grabbed, frame) = stream.read()
            # break if NoneType
            if not grabbed:
                break
            
            pipe.put(frame)


            # reducer frames size if you want more performance otherwise comment this line
            #frame = await reducer(frame, percentage=30)  # reduce frame by 30%


            await asyncio.sleep(0.00001)
        # close stream
        stream.release()


    # create your own custom frame producer
    async def my_frame_producer2(self):

        # !!! define your second video source here !!!
        # Open any video stream such as "foo2.mp4"
        stream = cv2.VideoCapture("foo2.mp4")
        # loop over frames
        while True:
            # read frame from provided source
            (grabbed, frame) = stream.read()
            # break if NoneType
            if not grabbed:
                break

            # do something with your OpenCV frame here

            # reducer frames size if you want more performance otherwise comment this line
            frame = await reducer(frame, percentage=30)  # reduce frame by 30%
            # handle JPEG encoding
            encodedImage = cv2.imencode(".jpg", frame)[1].tobytes()
            # yield frame in byte format
            yield (b"--frame\r\nContent-Type:video/jpeg2000\r\n\r\n" + encodedImage + b"\r\n")
            await asyncio.sleep(0.00001)
        # close stream
        stream.release()


    async def custom_video_response(self,scope):
        """
        Return a async video streaming response for `my_frame_producer2` generator
        """
        assert scope["type"] in ["http", "https"]
        await asyncio.sleep(0.00001)
        return StreamingResponse(
            my_frame_producer2(),
            media_type="multipart/x-mixed-replace; boundary=frame",
        )


 