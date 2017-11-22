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
        self.shapeCoordinates1 = shapeCoordinates1
        self.shapeCoordinates2 = shapeCoordinates2
        #self.triangle1 = np.array([shapeCoordinates1[0], shapeCoordinates1[1], (shapeCoordinates1[0][0], shapeCoordinates1[1][1])], dtype=np.int32)
        #self.triangle2 = np.array([shapeCoordinates2[0], shapeCoordinates2[1], (shapeCoordinates1[0][0], shapeCoordinates2[1][1])], dtype=np.int32)

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

        self.filteredImg = cv2.cvtColor(self.capturedFrame, colorScheme)  # Pane pilt etteantud värviskeemi
        cv2.ellipse(self.filteredImg,(self.shapeCoordinates1[0][0], self.shapeCoordinates1[1][1]), (180, 80),
                    180, 90, 0, (255,255,255), -1)
        self.filteredImg = cv2.cvtColor(self.capturedFrame, colorScheme)  # Pane pilt etteantud värviskeemi
        cv2.ellipse(self.filteredImg, (self.shapeCoordinates2[0][0], self.shapeCoordinates2[1][1]), (180, 80),
                    180, 90, 180, (255, 255, 255), -1)
        cv2.rectangle(self.filteredImg, (self.shapeCoordinates1[1][0], self.shapeCoordinates1[1][1] // 2),
                      (self.shapeCoordinates2[0][0], self.shapeCoordinates1[0][1] // 2), (255, 255, 255), -1)
        self.bw = cv2.cvtColor(self.capturedFrame, cv2.COLOR_BGR2GRAY)
        cv2.ellipse(self.bw, (self.shapeCoordinates1[1][0], self.shapeCoordinates1[0][1]), (180, 80),
                    180, 90, 0, (255, 255, 255), -1)
        cv2.rectangle(self.bw,(self.shapeCoordinates1[1][0],self.shapeCoordinates1[1][1]//2),
                      (self.shapeCoordinates2[0][0], self.shapeCoordinates1[0][1] // 2), (255,255,255), -1)
        self.filteredImg = cv2.cvtColor(self.capturedFrame, colorScheme)  # Pane pilt etteantud värviskeemi
        cv2.ellipse(self.bw, (self.shapeCoordinates2[1][0], self.shapeCoordinates2[0][1]), (180, 80),
                    180, 90, 180, (255, 255, 255), -1)

    def releaseCapture(self):
        # When everything done, release the capture
        self.cap.release()
