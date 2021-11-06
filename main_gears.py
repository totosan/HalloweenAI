#!/usr/local/python/bin/python

from Cam.ImageServer import ImageServer
from Gears.webGear_frames import gearIt
#from Gears.streamAsync import gearIt

def run():
    gear = gearIt(ImageServer)
    gear.run()

if __name__=="__main__":
    run()