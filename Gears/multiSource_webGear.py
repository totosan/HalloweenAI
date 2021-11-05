# import necessary libs
import uvicorn, asyncio, cv2
import numpy as np
from av import VideoFrame
from aiortc import VideoStreamTrack
from vidgear.gears.asyncio import WebGear_RTC
from vidgear.gears.asyncio.helper import reducer

# frame concatenator
def get_conc_frame(frame1, frame2):
    h1, w1 = frame1.shape[:2]
    h2, w2 = frame2.shape[:2]

    # create empty matrix
    vis = np.zeros((max(h1, h2), w1 + w2, 3), np.uint8)

    # combine 2 frames
    vis[:h1, :w1, :3] = frame1
    vis[:h2, w1 : w1 + w2, :3] = frame2

    return vis

# create your own Bare-Minimum Custom Media Server
class Custom_RTCServer(VideoStreamTrack):
    """
    Custom Media Server using OpenCV, an inherit-class
    to aiortc's VideoStreamTrack.
    """

    def __init__(self, source1=None, source2=None):

        # don't forget this line!
        super().__init__()

        # check is source are provided
        if source1 is None or source2 is None:
            raise ValueError("Provide both source")

        # initialize global params
        # define both source here
        self.stream1 = cv2.VideoCapture(source1)
        self.stream2 = cv2.VideoCapture(source2)

    
    async def recv(self):
        """
        A coroutine function that yields `av.frame.Frame`.
        """
        # don't forget this function!!!

        # get next timestamp
        pts, time_base = await self.next_timestamp()

        # read video frame
        (grabbed1, frame1) = self.stream1.read()
        (grabbed2, frame2) = self.stream2.read()

        # if NoneType
        if not grabbed1 or not grabbed2:
            return None
        else:
            print("Got frames")

        # concatenate frame
        frame = get_conc_frame(frame1, frame2)

        # reducer frames size if you want more performance otherwise comment this line
        #frame = await reducer(frame, percentage=30)  # reduce frame by 30%

        # contruct `av.frame.Frame` from `numpy.nd.array`
        av_frame = VideoFrame.from_ndarray(frame, format="bgr24")
        av_frame.pts = pts
        av_frame.time_base = time_base

        # return `av.frame.Frame`
        return av_frame

    def terminate(self):
        """
        Gracefully terminates VideoGear stream
        """
        # don't forget this function!!!

        # terminate
        if not (self.stream1 is None):
            self.stream1.release()
            self.stream1 = None

        if not (self.stream2 is None):
            self.stream2.release()
            self.stream2 = None

class gearIt(object):
    def __init__(self, *args):
        
        # initialize WebGear_RTC app without any source
        self.web = WebGear_RTC(logging=True)

    def run(self):
        # assign your custom media server to config with both adequate sources (for e.g. foo1.mp4 and foo2.mp4)
        self.web.config["server"] = Custom_RTCServer(
            source1="video.mp4", source2="http://192.168.0.128:8080/video"
        )

        # run this app on Uvicorn server at address http://localhost:8000/
        uvicorn.run(self.web(), host="0.0.0.0", port=8000)

        # close app safely
        self.web.shutdown()
        