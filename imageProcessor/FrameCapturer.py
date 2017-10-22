import cv2
import numpy as np

class FrameCapturer:

    def __init__(self, camID):
        self.cap = cv2.VideoCapture(camID)
        self.cap.set(cv2.CAP_PROP_FPS, 120)
        self.capturedFrame = None
        self.filteredImg = None
        self.height = None
        self.width = None
        self.bw = None
        # cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1080)
        # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    # Captures an image and returns the original frame and a filtered image.
    # colorScheme - the filter to be applied
    def capture(self, colorScheme):
        # Capture frame-by-frame
        ret, self.capturedFrame = self.cap.read()
        self.height, self.width, channels = self.capturedFrame.shape
        # Check whether the frame exists.
        if not ret:
            print("Cannot read the frame")
            return

        self.filteredImg = cv2.cvtColor(self.capturedFrame, colorScheme)  # Pane pilt etteantud värviskeemi
        self.bw = cv2.cvtColor(self.capturedFrame, cv2.COLOR_BGR2GRAY)

    def releaseCapture(self):
        # When everything done, release the capture
        self.cap.release()
