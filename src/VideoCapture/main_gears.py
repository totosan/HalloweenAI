import sys
sys.path.append("../")
from Gears.VideoProcessor import VideoProcessor
from Tracking.FaceDetector_cv2 import FaceDetectorDnn

def run():
    detector = FaceDetectorDnn()
    gear = VideoProcessor( detector)
    gear.run()

if __name__=="__main__":
    run()