#!/usr/local/python/bin/python

from Cam.ImageServer import ImageServer
from Gears.VideoProcessor import VideoProcessor
from Tracking.FaceAPI import FaceDetection
def run():
    detector = FaceDetection()
    gear = VideoProcessor(ImageServer, detector)
    gear.run()

if __name__=="__main__":
    run()