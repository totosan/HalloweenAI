"""Difference from running average
with multiprocessing and shared memory."""

import multiprocessing
import datetime
import time
import sys
import cv2
import numpy as np
import mpipe
import sharedmem

import coils
import utils

DEVICE   = "video.mp4"
DURATION = 20.0  # In seconds.

# Create a process-shared (common) table keyed on timestamps
# and holding references to allocated memory.
common = multiprocessing.Manager().dict()

class Step1(mpipe.OrderedWorker):
    def __init__(self):
        self.image_acc = None  # Maintain accumulation of thresholded differences.
        self.tstamp_prev = None  # Keep track of previous iteration's timestamp.

    def doTask(self, tstamp):
        image = common[tstamp]['image_in']

        # Initalize accumulation if so indicated.
        if self.image_acc is None:
            self.image_acc = np.empty(np.shape(image))

      
        # Write diff image (actually, reference thereof) to process-shared table.
        hello = common[tstamp]
        hello['image_diff'] = image
        common[tstamp] = hello
        
        # Propagate result to the next stage.
        self.putResult(tstamp)

        
# Monitor framerates for the given seconds past.
framerate = coils.RateTicker((1,5,10))


def step2(tstamp):
    """Display the image, stamped with framerate."""
    fps_text = '{:.2f}, {:.2f}, {:.2f} fps'.format(*framerate.tick())
    utils.writeOSD(common[tstamp]['image_diff'], (fps_text,))
  
    return tstamp

# Assemble the pipeline.
stage1 = mpipe.Stage(Step1)
stage2 = mpipe.OrderedStage(step2)
stage1.link(stage2)
pipe = mpipe.Pipeline(stage1)

# Create an auxiliary process (modeled as a one-task pipeline)
# that simply pulls results from the image processing pipeline, 
# and deallocates associated shared memory after allowing
# the designated amount of time to pass.
def deallocate(age):
    for tstamp in pipe.results():
        delta = datetime.datetime.now() - tstamp
        duration = datetime.timedelta(seconds=age) - delta
        if duration > datetime.timedelta():
            time.sleep(duration.total_seconds())
        del common[tstamp]
pipe2 = mpipe.Pipeline(mpipe.UnorderedStage(deallocate))
pipe2.put(2)  # Start it up right away.

# Create the OpenCV video capture object.
cap = cv2.VideoCapture(DEVICE)
#cap.set(3, WIDTH)
#cap.set(4, HEIGHT)

# Run the video capture loop, feeding the image processing pipeline.
now = datetime.datetime.now()
end = now + datetime.timedelta(seconds=DURATION)
while end > now:
    now = datetime.datetime.now()
    hello, image = cap.read()
    
    # Allocate shared memory for a copy of the input image.
    image_in = sharedmem.empty(np.shape(image), image.dtype)
    
    # Copy the input image to it's shared memory version.
    image_in[:] = image.copy()
    
    # Add image to process-shared table.
    common[now] = {'image_in' : image_in}

    # Feed the pipeline.
    pipe.put(now)

# Signal pipelines to stop, and wait for deallocator
# to free all memory.
pipe.put(None)
pipe2.put(None)
for result in pipe2.results():
    pass