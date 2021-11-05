# import required libraries
import uvicorn
from vidgear.gears.asyncio import WebGear_RTC

class gearIt(object):
    def __init__(self, *args):
        # various performance tweaks
        self.options = {
            "frame_size_reduction": 25,
            "enable_live_braodcast":True,
        }   


    def run(self):
        # initialize WebGear_RTC app
        #web = WebGear_RTC(source="video.mp4", logging=True, **self.options)
        web = WebGear_RTC(source="http://192.168.0.128:8080/video", logging=True, **self.options)
        
        # run this app on Uvicorn server at address http://localhost:8000/
        uvicorn.run(web(), host="0.0.0.0", port=8000)

        # close app safely
        web.shutdown()