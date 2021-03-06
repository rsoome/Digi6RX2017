import cv2
import numpy as np

class FrameCapturer:

    def __init__(self, camID, shapeCoordinates1, shapeCoordinates2):
        self.camID = camID
        self.cap = cv2.VideoCapture(camID)
        self.cap.set(cv2.CAP_PROP_FPS, 120)
        self.capturedFrame = None
        self.filteredImg = None
        self.height = None
        self.width = None
        self.bw = None

    # Captures an image and returns the original frame and a filtered image.
    # colorScheme - the filter to be applied
    def capture(self, colorScheme):
        # Capture frame-by-frame
        ret, self.capturedFrame = self.cap.read()
        # Check whether the frame exists.
        if not ret:
            print("Cannot read the frame")
            self.cap = cv2.VideoCapture(self.camID)
            return
        self.height, self.width, channels = self.capturedFrame.shape

        cv2.ellipse(self.capturedFrame, ((self.width // 2 - 10), self.height), ((self.width // 3), 60), 180, 180, 0,
                    (255, 255, 255), -1)
        self.filteredImg = cv2.cvtColor(self.capturedFrame, colorScheme)  # Pane pilt etteantud värviskeemi
        self.bw = cv2.cvtColor(self.capturedFrame, cv2.COLOR_BGR2GRAY)

    def releaseCapture(self):
        # When everything done, release the capture
        self.cap.release()
