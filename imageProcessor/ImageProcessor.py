import threading
import cv2

# Class for processing images. It is expected to be created by createImageProcessor() function.
class ImageProcessor:
    # img - Mask of the object of which's coordinates are to be found
    # verticalLowerBound - Image global vertical lower bound of the image part.
    # horiZontalLowerBound - Image global horizontal lower bound of the image part.
    # minSize - The minimum size of the object to be found.
    # cancelToken - token indicating whether the job should be cancelled
    # obejct - the object into which to write the coordinates found
    # threadID - ID of the thread
    def __init__(self, img, verticalLowerBound, horizontalLowerBound, minSize, cancelToken, target, threadID):
        self.img = img
        self.verticalLowerBound = verticalLowerBound
        self.horizontalLowerBound = horizontalLowerBound
        self.minSize = minSize
        self.cancelToken = cancelToken
        self.cancellationLock = threading.Lock()
        self.obj = target
        self.threadID = threadID

    # Finds from the given mask a blob at least as big as the minSize
    def findObjectCoordinates(self):
        # Find blobs
        image, cnts, hirearchy = cv2.findContours(self.img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # If no blob is found, cancel
        if len(cnts) == 0:
            return

        # Find the biggest blob
        c = max(cnts, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(c)

        # print(x)
        # print(y)

        # If the rectangle surrounding the biggest blob is big enough, try to write it's coordinates into the object given
        if w * h >= self.minSize:
            # Check, whether another thread has signalled a cancellation of the job, and stop if the job is cancelled
            if self.cancelToken.isCanceled:
                return

            # print(self.threadID)

            # Lock the cancellation token to cancel all other jobs running
            self.cancellationLock.acquire()
            self.cancelToken.cancel()

            # Write the found coordinates into the given object and release the cancellation token
            self.obj.setBounds([self.horizontalLowerBound + x, self.horizontalLowerBound + x + w],
                               [self.verticalLowerBound + y, self.verticalLowerBound + y + h])
            #print(self.obj.verticalBounds)
            self.cancellationLock.release()