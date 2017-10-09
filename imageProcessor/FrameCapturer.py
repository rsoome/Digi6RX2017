import cv2

class FrameCapturer:

    def __init__(self, camID):
        self.cap = cv2.VideoCapture(camID)
        self.cap.set(cv2.CAP_PROP_FPS, 120)
        self.capturedFrame = None
        self.filteredImg = None
        # cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1080)
        # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    # Captures an image and returns the original frame and a filtered image.
    # colorScheme - the filter to be applied
    def capture(self, colorScheme):
        # Capture frame-by-frame
        ret, self.capturedFrame = self.cap.read()
        # Check whether the frame exists.
        if not ret:
            print("Cannot read the frame")
            return

        self.filteredImg = cv2.cvtColor(self.capturedFrame, colorScheme)  # Pane pilt etteantud värviskeemi

    def releaseCapture(self):
        # When everything done, release the capture
        self.cap.release()