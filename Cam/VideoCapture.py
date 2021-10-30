# To make python 2 and python 3 compatible code
from __future__ import division
from __future__ import absolute_import

try:
	import ptvsd
	__myDebug__ = True 
	print("Please attach debugger!")
	ptvsd.enable_attach(('0.0.0.0',  5678))   
	#ptvsd.wait_for_attach()
except ImportError:
	__myDebug__ = False
	
import cv2
import numpy as np
import requests
import time
import json
import io
import os
import signal
import urllib.request as urllib2


# Vision imports
from Cam.ImageServer import ImageServer
from Cam.VideoStream import VideoStream


class VideoCapture(object):

	def __init__(
			self,
			videoPath="",
			verbose=True,
			videoW=0,
			videoH=0,
			fontScale=1.0,
			inference=True,
			confidenceLevel=0.5,
			detectionSampleRate = 10,
			imageProcessingEndpoint=""):

		self.config = self.GetConfig()
		self.features = self.GetFeaturesFromConfig(self.config)
		self.videoPath = videoPath
		self.verbose = verbose
		self.videoW = videoW
		self.videoH = videoH
		self.inference = inference
		self.confidenceLevel = confidenceLevel
		self.useStream = False
		self.useStreamHttp = False
		self.useMovieFile = False
		self.frameCount = 0
		self.vStream = None
		self.vCapture = None
		self.displayFrame = None
		self.fontScale = float(fontScale)
		self.captureInProgress = False
		self.imageResp = None
		self.url = ""
		self.detectionSampleRate = detectionSampleRate
		self.imageProcessingEndpoint = imageProcessingEndpoint

		self.Mouse = None
		self.Drawer = []
		self.ORB = cv2.ORB_create()

		if 'orb' in self.features:
			self.refImage = cv2.imread('Cam/BienenDominik.jpg',0)

		print("VideoCapture::__init__()")
		print("OpenCV Version : %s" % (cv2.__version__))
		print("===============================================================")
		print("Initialising Video Capture with the following parameters: ")
		print("   - Video path      : " + self.videoPath)
		print("   - Video width     : " + str(self.videoW))
		print("   - Video height    : " + str(self.videoH))
		print("   - Font Scale      : " + str(self.fontScale))
		print("   - Inference?      : " + str(self.inference))
		print("   - ConficenceLevel : " + str(self.confidenceLevel))
		print("   - Dct smpl rate   : " + str(self.detectionSampleRate))
		print("   - Imageproc.Endpt.: " + str(self.imageProcessingEndpoint))
		print("")

		self.imageServer = ImageServer(8000, self)
		self.imageServer.start()


	def GetConfig(self):
		with open('config.json') as json_file:
			config = json.load(json_file)
			print(f"Current config:\r\n{config}")
			return config

	def GetFeaturesFromConfig(self, config):
		features = []
		for f in config['features']:
			if f['value'] == True:
				features.append(f['name'])
		print("Features: ",features)
		return features

	def __IsCaptureDev(self, videoPath):
		try:
			return '/dev/video' in videoPath.lower()
		except ValueError:
			return False

	def __IsHttp(self, videoPath):
		try:
			if "http" in videoPath and ":8080" in videoPath:
				return True
			return False
		except:
			return False

	def __IsRtsp(self, videoPath):
		try:
			if 'rtsp:' in videoPath.lower() or '/api/holographic/stream' in videoPath.lower():
				return True
		except ValueError:
			return False

	def __IsYoutube(self, videoPath):
		try:
			if 'www.youtube.com' in videoPath.lower() or 'youtu.be' in videoPath.lower():
				return True
			else:
				return False
		except ValueError:
			return False

	def __enter__(self):

		if self.verbose:
			print("videoCapture::__enter__()")

		self.setVideoSource(self.videoPath)

		return self

	def setVideoSource(self, newVideoPath):

		if self.captureInProgress:
			self.captureInProgress = False
			time.sleep(1.0)
			if self.vCapture:
				self.vCapture.release()
				self.vCapture = None
			elif self.vStream:
				self.vStream.stop()
				self.vStream = None
			elif self.imageResp:
				self.imageResp.close()
				self.imageResp = None

		if self.__IsRtsp(newVideoPath):
			print("\r\n===> RTSP Video Source")

			self.useStream = True
			self.useStreamHttp = False
			self.useMovieFile = False
			self.videoPath = newVideoPath

			if self.vStream:
				self.vStream.start()
				self.vStream = None

			if self.vCapture:
				self.vCapture.release()
				self.vCapture = None

			self.vStream = VideoStream(newVideoPath).start()
			# Needed to load at least one frame into the VideoStream class
			time.sleep(1.0)
			self.captureInProgress = True

		elif self.__IsHttp(newVideoPath):
			print("IsHttp")
			# Use urllib to get the image and convert into a cv2 usable format
			self.url = newVideoPath
			self.useStreamHttp = True
			self.useStream = False
			self.useMovieFile = False
			self.captureInProgress = True

		elif self.__IsYoutube(newVideoPath):
			print("\r\n===> YouTube Video Source")
			self.useStream = False
			self.useStreamHttp = False
			self.useMovieFile = True
			# This is video file
			self.downloadVideo(newVideoPath)
			self.videoPath = newVideoPath
			if self.vCapture.isOpened():
				self.captureInProgress = True
			else:
				print(
					"===========================\r\nWARNING : Failed to Open Video Source\r\n===========================\r\n")

		elif self.__IsCaptureDev(newVideoPath):
			print("===> Webcam Video Source")
			if self.vStream:
				self.vStream.start()
				self.vStream = None

			if self.vCapture:
				self.vCapture.release()
				self.vCapture = None

			self.videoPath = newVideoPath
			self.useMovieFile = False
			self.useStream = False
			self.useStreamHttp = False
			self.vCapture = cv2.VideoCapture(newVideoPath)
			if self.vCapture.isOpened():
				self.captureInProgress = True
			else:
				print(
					"===========================\r\nWARNING : Failed to Open Video Source\r\n===========================\r\n")
		else:
			print(
				"===========================\r\nWARNING : No Video Source\r\n===========================\r\n")
			self.useStream = False
			self.useYouTube = False
			self.vCapture = None
			self.vStream = None
		return self

	def downloadVideo(self, videoUrl):
		if self.captureInProgress:
			bRestartCapture = True
			time.sleep(1.0)
			if self.vCapture:
				print("Relase vCapture")
				self.vCapture.release()
				self.vCapture = None
		else:
			bRestartCapture = False

		if os.path.isfile('/app/video.mp4'):
			os.remove("/app/video.mp4")

		print("Start downloading video")
		os.system("youtube-dl -o /app/video.mp4 -f mp4 " + videoUrl)
		print("Download Complete")
		self.vCapture = cv2.VideoCapture("/app/video.mp4")
		time.sleep(1.0)
		self.frameCount = int(self.vCapture.get(cv2.CAP_PROP_FRAME_COUNT))

		if bRestartCapture:
			self.captureInProgress = True

	def get_display_frame(self):
		return self.displayFrame

	def videoStreamReadTimeoutHandler(signum, frame):
		raise Exception("VideoStream Read Timeout")

	def start(self):
		while True:
			if self.captureInProgress:
				self.__Run__()

			if not self.captureInProgress:
				time.sleep(1.0)

	def getColorOnMousePosition(self,frame, mouseEventData):
		(x,y) = (mouseEventData['x'],mouseEventData['y'])
		pixel = frame[y,x]
		bgr = [int(pixel[0]),int(pixel[1]),int(pixel[2])]
		hsv = cv2.cvtColor( np.uint8([[bgr]]), cv2.COLOR_BGR2HSV)[0][0]
		print(f'color - BGR:{bgr} / HSV:{hsv} \t pos:{(x,y)}')
		draw = (x,y,bgr, hsv)
		self.Drawer.append(draw)
		return draw

	def setHsvRange(self,hsv):	
		corridor = 10
		hMin = (hsv[0]-corridor, 0)[hsv[0]-corridor <= 0]
		sMin = (hsv[1]-corridor*2, 0)[hsv[1]-corridor*2 <= 0]
		vMin = (hsv[2]-corridor*3, 0)[hsv[2]-corridor*3 <= 0]

		hMax = (hsv[0]+corridor, 179)[hsv[0]+corridor > 179]
		sMax = 255
		vMax = 255

		hsvMin = (hMin, sMin, vMin)
		hsvMax = (hMax, sMax, vMax)
		print('HSV Min',hsvMin)	
		print('HSV Max',hsvMax)	
		rangeMin = np.array([hsvMin[0], hsvMin[1], hsvMin[2]], np.uint8)
		rangeMax = np.array([hsvMax[0], hsvMax[1], hsvMax[2]], np.uint8)
		print(f'Range Min: {rangeMin} / Range Max: {rangeMax}')
		return rangeMin, rangeMax

	def GetCorrespondingFeatures(self, frame):
		kpRef, destRef = self.ORB.detectAndCompute(self.refImage,None)
		kpTarget, desTarget = self.ORB.detectAndCompute(frame, None)
		#frame=cv2.drawKeypoints(frame, kp, None, color=(0,255,0), flags=0)
		bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
		matches = bf.match(destRef, desTarget)
		matches = sorted(matches, key = lambda x:x.distance)
		return cv2.drawMatches(self.refImage,kpRef,frame,kpTarget,matches[:10],None, flags=2)


	def __Run__(self):

		print("===============================================================")
		print("videoCapture::__Run__()")
		print("   - Stream          : " + str(self.useStream))
		print("   - useMovieFile    : " + str(self.useMovieFile))

		cameraH = 0
		cameraW = 0
		frameH = 0
		frameW = 0
		
		if self.useStream and self.vStream:
			cameraH = int(self.vStream.stream.get(cv2.CAP_PROP_FRAME_HEIGHT))
			cameraW = int(self.vStream.stream.get(cv2.CAP_PROP_FRAME_WIDTH))
		elif self.useStream == False and self.vCapture:
			cameraH = int(self.vCapture.get(cv2.CAP_PROP_FRAME_HEIGHT))
			cameraW = int(self.vCapture.get(cv2.CAP_PROP_FRAME_WIDTH))
		elif self.useStreamHttp == True:
			cameraW = 1280
			cameraH = 960
		else:
			print("Error : No Video Source")
			return

		if self.videoW != 0 and self.videoH != 0 and self.videoH != cameraH and self.videoW != cameraW:
			needResizeFrame = True
			frameH = self.videoH
			frameW = self.videoW
		else:
			needResizeFrame = False
			frameH = cameraH
			frameW = cameraW

		if needResizeFrame:
			print("Original frame size  : " +
				  str(cameraW) + "x" + str(cameraH))
			print("     New frame size  : " + str(frameW) + "x" + str(frameH))
			print("             Resize  : " + str(needResizeFrame))
		else:
			print("Camera frame size    : " +
				  str(cameraW) + "x" + str(cameraH))
			print("       frame size    : " + str(frameW) + "x" + str(frameH))

		# Check camera's FPS
		if self.useStream:
			cameraFPS = int(self.vStream.stream.get(cv2.CAP_PROP_FPS))
		elif self.useStreamHttp:
			cameraFPS = 30
		else:
			cameraFPS = int(self.vCapture.get(cv2.CAP_PROP_FPS))

		if cameraFPS == 0:
			print("Error : Could not get FPS")
			raise Exception("Unable to acquire FPS for Video Source")

		print("Frame rate (FPS)     : " + str(cameraFPS))

		currentFPS = cameraFPS
		perFrameTimeInMs = 1000 / cameraFPS

		signal.signal(signal.SIGALRM, self.videoStreamReadTimeoutHandler)

		rangeMin = np.array([])
		rangeMax = np.array([])

		# Ãrea mÃ­nima Ã¡ ser detectada
		minArea = 50

		while True:

			# Get current time before we capture a frame
			tFrameStart = time.time()
			if not self.captureInProgress:
				print("broke frame processing for new videosource...")
				break

			if self.useMovieFile:
				currentFrame = int(self.vCapture.get(cv2.CAP_PROP_POS_FRAMES))
				if currentFrame >= self.frameCount:
					self.vCapture.set(cv2.CAP_PROP_POS_FRAMES, 0)

			try:
				# Read a frame
				if self.useStream:
					# Timeout after 10s
					signal.alarm(10)
					frame = self.vStream.read()
					signal.alarm(0)
					
				elif self.useStreamHttp:
					self.imageResp = urllib2.urlopen(self.url)
					imgNp = np.array(bytearray(self.imageResp.read()),dtype=np.uint8)
					frame = cv2.imdecode(imgNp,-1)
					
				else:
					frame = self.vCapture.read()[1]
			except Exception as e:
				print("ERROR : Exception during capturing")
				raise(e)

			# Resize frame if flagged
			if needResizeFrame:
				frame = cv2.resize(frame, (self.videoW, self.videoH))

			# Run Object Detection -- GUARD
			#if self.inference:
				#yoloDetections = self.yoloInference.runInference(frame, frameW, frameH, self.confidenceLevel)

			########
			# Do all teh extra stuff here
			########
			
			if 'orb' in self.features:
				frame = self.GetCorrespondingFeatures(frame)

			if 'click' in self.features:
				lastDraw = None
				if self.Mouse and self.Mouse['type'] == 'click':
					lastDraw = self.getColorOnMousePosition(frame, self.Mouse)
					self.Mouse = None
					rangeMin, rangeMax = self.setHsvRange(lastDraw[3])
					print(f'Range Min: {rangeMin} / Range Max: {rangeMax}')
				for click in self.Drawer:
					cv2.circle(frame,(click[0],click[1]),3,(0,200,20),-1)

			if 'binarizer' in self.features:
				if rangeMin.any() and rangeMax.any():
					imgHSV = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)	
					
					imgThresh = cv2.inRange(imgHSV, rangeMin, rangeMax)
					imgErode = cv2.erode(imgThresh, None, iterations = 3)
					moments = cv2.moments(imgErode, True)
					if moments['m00'] >= minArea:
						x = moments['m10'] / moments['m00']
						y = moments['m01'] / moments['m00']
						cv2.circle(frame, (int(x), int(y)), 5, (0, 255, 0), -1)
						self.driveRobot(moments['m00'],int(x),int(y))
					#frame = cv2.bitwise_and(frame,frame, mask=imgThresh)
					frame = cv2.rectangle(frame, (0,0),(160,480),(0,255,0),1)
					frame = cv2.rectangle(frame, (480,0),(640,480),(0,255,0),1)

			# Calculate FPS
			timeElapsedInMs = (time.time() - tFrameStart) * 1000
			currentFPS = 1000.0 / timeElapsedInMs

			if (currentFPS > cameraFPS):
				# Cannot go faster than Camera's FPS
				currentFPS = cameraFPS

			# Add FPS Text to the frame
			cv2.putText(frame, "FPS " + str(round(currentFPS, 1)), (10, int(30 *
																			self.fontScale)), cv2.FONT_HERSHEY_SIMPLEX, self.fontScale, (0, 0, 255), 2)

			self.displayFrame = cv2.imencode('.jpg', frame)[1].tobytes()

			timeElapsedInMs = (time.time() - tFrameStart) * 1000

			if False and (1000 / cameraFPS) > timeElapsedInMs:
				# This is faster than image source (e.g. camera) can feed.
				waitTimeBetweenFrames = perFrameTimeInMs - timeElapsedInMs
				# if self.verbose:
				print("  Wait time between frames :" + str(int(waitTimeBetweenFrames)))
				time.sleep(waitTimeBetweenFrames/1000.0)

	def __exit__(self, exception_type, exception_value, traceback):

		if self.vCapture:
			self.vCapture.release()

		self.imageServer.close()
		cv2.destroyAllWindows()
