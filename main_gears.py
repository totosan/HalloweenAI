#!/usr/local/python/bin/python

from Cam.ImageServer import ImageServer
from Gears.VideoProcessor import VideoProcessor
from Tracking.FaceDetector_cv2 import FaceDetectorDnn
def run():
    detector = FaceDetectorDnn()
    gear = VideoProcessor(ImageServer, detector)
    gear.run()

if __name__=="__main__":
    run()