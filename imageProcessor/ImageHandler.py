import time

from imageProcessor import ImageProcessor
import numpy as np
import cv2
from cancellationToken import CancellationToken
import threading
from timer import Timer

class ImageHandler:

    def __init__(self, multiThreading, frame, objects, imageMinArea, socketData):
        self.multiThreading = multiThreading
        self.frame = frame
        self.objects = objects
        self.imageMinArea = imageMinArea
        self.socketData = socketData
        self.FRAMEUPDATEPERIOD = 1 / 120

    def generateMask(self, targetObject):
        filteredImg = self.frame.filteredImg
        if filteredImg is not None:
            hsvLowerRange = targetObject.hsvLowerRange
            hsvUpperRange = targetObject.hsvUpperRange
            try:
                if hsvLowerRange is not None and hsvUpperRange is not None:
                    thresh = cv2.inRange(filteredImg, hsvLowerRange, hsvUpperRange)
                    #print(targetObject.id, "'s mask:", thresh)
                    targetObject.mask = thresh
            except Exception as e:
                print(e)
                print("filteredImg: ", filteredImg)
                print("hsvLowerRange, ", hsvLowerRange)
                print("hsvUpperRange", hsvUpperRange)
        else:
            print("No frame captured.")
	

    # Creates an imageProcessor
    # rocessor object and runs it's findObject function.
    # The funtion is meant to be ran on multiple threads processing different parts of a picture but can be used on a single
    # thread with the whole picture.
    # verticalLowerBound - image's vertical (y-axis) global lower bound of the part of the imgae being processed.
    # In case the whole picture is being processed it is to be assigned the value 0.
    # horizontalLowerBound - image's horizontal (x-axis) global lower bound of the part of the image being processed.
    # minSize - The minimum area of the rectangle surrounding the object. Objects smaller than this are not considered valid.
    # cancellationToken - A token that signals the parallel threads whether the object has been already found.
    # target - the object into which the found coordinates will be inserted.
    # threadID - the ID by which the parallel threads will be identified. Can be any value.
    def createImageProcessor(self, verticalLowerBound, horizontalLowerBound, cancellationToken, target, threadID):
        imgProc = ImageProcessor.ImageProcessor(verticalLowerBound, horizontalLowerBound, cancellationToken, target,
                                                threadID)
        imgProc.findObjectCoordinates()

    # Blurs the image to remove noise
    def blur(self, img):
        kernel = np.ones((50, 50), np.uint8)  # //TODO: Find values to put in the kernel
        closing = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
        gauss = cv2.GaussianBlur(img, (5, 5), 0)
        return gauss

    # Finds object coordinates in the given picture
    # img - the mask from which to find the coordinates
    # verticalLowerBound - the image global vertical lower bound
    # horizontalLowerbound - the image global horizontal lower bound
    def findObject(self, verticalLowerBound, horizontalLowerBound, obj):
        obj.resetBounds()
        c = CancellationToken.CancellationToken()
        self.createImageProcessor(verticalLowerBound, horizontalLowerBound, c, obj, "0")

    #TODO: CURRENTLY DOES NOT WORK, MIGHT DO MORE HARM THAN GOOD EITHER WAY
    # Divides the given image into parts recursively. Then feeds the found parts to multiple threads to be processed for
    # object coordinates.
    # img - A mask of thresholded colors from which the blobs are to be found
    # verticalLowerBound - The image global vertical lower bound of img. On first iteration it is to be set 0.
    # verticalUpperBound - The image global vertical lupper bound of img. On first iteration it is to be set image height.
    # verticalLowerBound - The image global horizontal lower bound of img. On first iteration it is to be set 0.
    # verticalUpperBound - The image global horizontal lupper bound of img. On first iteration it is to be set image width.
    # minobjectSize - The minimum object size which is considered a valid object. On each recursive call the minObjectSize is
    # multiplied by 3 as the img size is divided by three.
    # minImgArea - the condition to exit the recursion. Image shall not be divided when it's size is smaller than this value.
    # scanOrder - the order, in which the parts of the image are fed to threads. Below is a diagram of the divison of the image
    # each divided part has an ID which are given on the diagram. The scanOrder is expected to be an integer array of some
    # permutation of these IDs.
    #
    # (0,0)---------------------------------- verdicalLowerBound=vLB
    # |           |             |           |
    # |     6     |      7      |      8    |
    # |           |             |           |
    # |-----------|-------------|-----------| vLB+(vUB-vLB)/3
    # |           |             |           |
    # |     3     |      4      |      5    |
    # |           |             |           |
    # |-----------|-------------|-----------| vLB+2*((vUB-vLB)/3)
    # |           |             |           |
    # |     0     |      1      |      2    |
    # |           |             |           |
    # --------------------------------------- verticalUpperBound=vUB
    # ^hLB+(hUB-hLB)/3   hLB+2*((hUB-hLB)/3)^
    # ^                                     ^
    # horizontalLowerBound=hLB      horizontalUpperBound=hUB
    def findObjectMultithreaded(self, verticalLowerBound, verticalUpperBound, horizontalLowerBound,
                                horizontalUpperBound, minObjectSize, minImgArea, scanOrder, obj):
        obj.resetBounds()

        horizontalBounds = None
        verticalBounds = None

        verticalThird = (verticalLowerBound + (verticalUpperBound - verticalLowerBound) // 3)
        verticalTwoThirds = (verticalLowerBound + 2 * (verticalUpperBound - verticalLowerBound) // 3)
        horizontalThird = (horizontalLowerBound + (horizontalUpperBound - horizontalLowerBound) // 3)
        horizontalTwoThirds = (horizontalLowerBound + 2 * (horizontalUpperBound - horizontalLowerBound) // 3)

        # Define the division boundaries
        verticalLowerBounds = [verticalTwoThirds, verticalTwoThirds, verticalTwoThirds,
                               verticalThird, verticalThird, verticalThird,
                               verticalLowerBound, verticalLowerBound, verticalLowerBound]

        verticalUpperBounds = [verticalUpperBound, verticalUpperBound, verticalUpperBound,
                               verticalTwoThirds, verticalTwoThirds, verticalTwoThirds,
                               verticalThird, verticalThird, verticalThird]

        horizontalLowerBounds = [horizontalLowerBound, horizontalThird, horizontalTwoThirds,
                                 horizontalLowerBound, horizontalThird, horizontalTwoThirds,
                                 horizontalLowerBound, horizontalThird, horizontalTwoThirds]

        horizontalUpperBounds = [horizontalThird, horizontalTwoThirds, horizontalUpperBound,
                                 horizontalThird, horizontalTwoThirds, horizontalUpperBound,
                                 horizontalThird, horizontalTwoThirds, horizontalUpperBound]

        # If the image area is bigger than minImgArea, go into recursion to divide the image smaller
        if ((verticalUpperBound - verticalLowerBound) * (horizontalUpperBound - horizontalLowerBound) > minImgArea):
            for i in range(len(scanOrder)):
                #            cv2.rectangle(mainImg, (horizontalLowerBounds[i], verticalUpperBounds[i]), (horizontalUpperBounds[i], verticalLowerBounds[i]),
                #                          (0, 0, 255), 1)

                # By the scan order divide each part of the image recursively
                self.findObjectMultithreaded(verticalLowerBounds[scanOrder[i]], verticalUpperBounds[scanOrder[i]],
                                             horizontalLowerBounds[scanOrder[i]], horizontalUpperBounds[scanOrder[i]],
                                             minObjectSize * 3, minImgArea, scanOrder, obj)

                horizontalBounds, verticalBounds = obj.getBounds()
                # If an object was found by the called recursion, return its coordinates
                if horizontalBounds is not None and verticalBounds is not None:
                    return

        # Create an object and a cancellation token for image processor
        cToken = CancellationToken.CancellationToken()

        # Send each part of the image to a separate thread in the order specified by the caller of the funtion
        for i in range(len(scanOrder)):

            # If an object has been found, return
            if horizontalBounds is not None and verticalBounds is not None:
                return
            t = threading.Thread(target=self.createImageProcessor(verticalLowerBounds[scanOrder[i]],
                                                                  horizontalLowerBounds[scanOrder[i]], cToken, obj, i))
            t.start()

    # Wrapper function to find coordinates of a given object
    # mainImg - the main frame which is showed in the main window
    # object - the mask from which the coordinates are to be detected
    # objectMinSize - the minimum size of the blob starting from which it's considered valid
    # imageMinArea - while the area of the part of the image being processed is bigger than this value, the image will be
    # divided recursively by the multi threaded function. If not specified or less then 0, no no recursive calls shall be done.
    # scanOrder - the order by which the image is fed to threads by multi threaded object finding function. More information
    # in findObjectMultithreaded() description.
    def detect(self, target):
        self.generateMask(target)
        if target.mask is not None:
            properties = target.mask.shape
            height = properties[0]
            width = properties[1]

            if self.imageMinArea < 1:
                imageMinArea = height * width + 1

            if self.multiThreading:
                self.findObjectMultithreaded(0, height, 0, width, target.minSize, self.imageMinArea, target.scanOrder, target)
            else:
                self.findObject(0, 0, target)
        else:
            print("Target has no mask.")

    def run(self):
        timer = Timer.Timer()
        framesCaptured = 0
        timePassed = 0
        while not self.socketData.stop:
            self.frame.capture(cv2.COLOR_BGR2HSV)
            for obj in self.objects:
                self.detect(obj)
                time.sleep(self.FRAMEUPDATEPERIOD)

            framesCaptured += 1
            timePassed += timer.reset()

            if framesCaptured >= 60:
                self.socketData.fps = int(framesCaptured/(timePassed/1000))
                framesCaptured = 0
                timePassed = 0

