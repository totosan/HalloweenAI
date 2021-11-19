# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import os
import random
import sys
import time
import json
import argparse
from netifaces import interfaces, ifaddresses, AF_INET

from Cam.VideoCapture import VideoCapture
from Cam.ImageServer import ImageServer
from FaceAPI import FaceDetection

try:
    import ptvsd
    __myDebug__ = True 
    ptvsd.enable_attach(('0.0.0.0',  5678))   
except ImportError:
    __myDebug__ = False
    

    
def ip4_addresses():
    ip_list = []
    if not __myDebug__:
        for interface in interfaces():
            for link in ifaddresses(interface)[AF_INET]:
                ip_list.append(link['addr'])
    return ip_list

def main(
        videoPath ="https://youtu.be/qEMC2bKC0wI",
        verbose = False,
        noIotHub = False,
        videoWidth = 160,
        videoHeight = 120,
        fontScale = 1.0,
        imageProcessingEndpoint=""
        ):

    global videoCapture
    injectedAnalyzer = FaceDetection()
    
    print("\nPython %s\n" % sys.version )
    with VideoCapture(videoPath, 
                        verbose,
                        videoWidth,
                        videoHeight,
                        fontScale,
                        imageProcessingEndpoint,
                        injectedAnalyzer=injectedAnalyzer,
                        callbackForFrames=injectedAnalyzer.detect_faces) as videoCapture:
        print(f'Analyzer: {injectedAnalyzer}')
        videoCapture.start()

def __convertStringToBool(env):
    if env in ['True', 'TRUE', '1', 'y', 'YES', 'Y', 'Yes']:
        return True
    elif env in ['False', 'FALSE', '0', 'n', 'NO', 'N', 'No']:
        return False
    else:
        raise ValueError('Could not convert string to bool.')

if __name__ == '__main__':
    try:
        VIDEO_PATH = os.getenv('VIDEO_PATH','/dev/video0')
        NOIOTHUB = __convertStringToBool(os.getenv('NOIOTHUB','True'))
        VERBOSE = __convertStringToBool(os.getenv('VERBOSE', 'False'))
        VIDEO_WIDTH = int(os.getenv('VIDEO_WIDTH', 0))
        VIDEO_HEIGHT = int(os.getenv('VIDEO_HEIGHT',0))
        FONT_SCALE = os.getenv('FONT_SCALE', 1)
        IMAGE_PROCESSING_ENDPOINT = os.getenv('IMAGE_PROCESSING_ENDPOINT')

    except ValueError as error:
        print(error )
        sys.exit(1)
        
    main(VIDEO_PATH, VERBOSE, NOIOTHUB, VIDEO_WIDTH, VIDEO_HEIGHT, FONT_SCALE, IMAGE_PROCESSING_ENDPOINT)



