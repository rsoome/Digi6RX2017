# coding=utf-8
import threading

import numpy as np
import cv2
from datetime import datetime
import serial
import math
import curses
import time
import sys

print("Running on Python " + sys.version)

# A token for indicating whether a thread should cancel it's job or not.
class CancellationToken:
    def __init__(self):
        self.isCanceled = False

    def cancel(self):
        self.isCanceled = True


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
            self.obj.horizontalBounds = [self.horizontalLowerBound + x, self.horizontalLowerBound + x + w]
            #print(self.obj.horizontalBounds)
            self.obj.verticalBounds = [self.verticalLowerBound + y, self.verticalLowerBound + y + h]
            #print(self.obj.verticalBounds)
            self.cancellationLock.release()


# The object class, in which you can hold the coordinates of an instance. For example - a ball or a gate
class Target:

    def __init__(self, hBounds, vBounds, targetID):
        self.horizontalBounds = hBounds
        self.verticalBounds = vBounds
        self.hsvLowerRange = np.array([255, 255, 255])  # HSV värviruumi alumine piir, hilisemaks filtreerimiseks TODO: Kirjuta faili
        self.hsvUpperRange = np.array([0, 0, 0])  # HSV värviruumi ülemine piir, hilisemaks filtreerimiseks TODO: Kirjuta faili
        self.id = targetID

    def getBounds(self):
        return self.horizontalBounds, self.verticalBounds

    # Writes new values into the variables containing threshholds of a given object.
    def updateThresholds(self, values):
        print("Updating " + str(self.id) + "'s thresholds.")
        # Check all the received values against current values and update if necessary
        for i in range(3):
            if values[i] < self.hsvLowerRange[i]:
                self.hsvLowerRange[i] = values[i]  # Kui väärtus on väiksem ,uuenda alumist piiri
            if values[i] > self.hsvUpperRange[i]:
                self.hsvUpperRange[i] = values[i]  # Kui väärtus on suurem, uuenda ülemist piiri

    def resetThreshHolds(self):
        self.hsvLowerRange = np.array(
            [255, 255, 255])
        self.hsvUpperRange = np.array(
            [0, 0, 0])

    def resetBounds(self):
        self.horizontalBounds = None
        self.verticalBounds = None

    def setBounds(self, hBounds, vBounds):
        self.horizontalBounds = hBounds
        self.verticalBounds = vBounds

class MBcomm:

    def __init__(self, target, baud):
        self.ser = serial.Serial(port=target, baudrate=baud, timeout=0.8)

    def __sendByte(self, cmd):
        if not self.ser.isOpen():
            self.ser.open()
        cmd += "\n"
        print(cmd)
        self.ser.write(cmd.encode())
        if self.ser.isOpen():
            self.ser.close()

    def __readBytes(self):
        if not self.ser.isOpen():
            self.ser.open()
        line = self.ser.readline().decode("ascii")
        if self.ser.isOpen():
            self.ser.close()
        return line

    def setMotorSpeed(self, speed0, speed1, speed2):
        self.__sendByte("sd" + str(speed0) + ":" + str(speed1) + ":" + str(speed2))

    def getMotorSpeed(self):
        self.__sendByte("sg")
        return self.__readBytes()

    def readInfrared(self):
        self.__sendByte("i")
        return self.__readBytes()

    def charge(self):
        self.__sendByte("c")

    def kick(self):
        self.__sendByte("k")

    def discharge(self):
        self.__sendByte("e")

    def enableFailSafe(self):
        self.__sendByte("f")

class MovementLogic:

    def __init__(self, mb):
        self.mb = mb

    def drive(self, speed):
        self.mb.setMotorSpeed(speed*(math.cos(1.04719755)), speed*(math.cos(-1.04719755 )), speed*(math.cos(0))) #60deg in rad

    def brake(self):
        speeds = self.mb.getMotorSpeed()
        speeds = speeds.split(":")
        self.mb.setMotorSpeed(int(speeds[0]), int(speeds[1]), int(speeds[2]))

    def rotate(self, speed):
        self.mb.setMotorSpeed(speed, speed, speed)

class ManualDrive:

    def __init__(self, move):
        print("Manual driving activated.")
        self.move = move

    def run(self):
        screen = curses.initscr()
        curses.cbreak()
        screen.keypad(1)

        keyStroke = ''
        while keyStroke != ord('q'):

            keyStroke = screen.getch()
            if keyStroke == ord('w'):
                move.drive(50)

            if keyStroke == ord('a'):
                move.rotate(-30)

            if keyStroke == ord('d'):
                move.rotate(30)

            if keyStroke == ord(' '):
                move.brake()
        print("Manual driving deactivated.")
        curses.endwin()

# For listening to referee signals
# TODO: Implement
class RefereeListener:


    def __init__(self):
        pass

# Contains the game logic
# TODO: Implement
class GameLogic:
    def __init__(self):
        pass

mbLocation = "/dev/ttyACM0"

camID = 0  # Kaamera ID TODO: Kirjuta faili
cap = cv2.VideoCapture(camID)
cap.set(cv2.CAP_PROP_FPS, 120)
#cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1080)
#cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)


multiThreading = True  # TODO: Kirjuta faili
textColor = (0, 0, 255)

selectedTarget = None

framesCaptured = 0
totalTimeElapsed = 0
fps = 0

hsv = None


# Creates an imageProcessor object and runs it's findObject function.
# The funtion is meant to be ran on multiple threads processing different parts of a picture but can be used on a single
# thread with the whole picture.
# img - (the part of) the image to be processed
# verticalLowerBound - image's vertical (y-axis) global lower bound of the part of the imgae being processed.
# In case the whole picture is being processed it is to be assigned the value 0.
# horizontalLowerBound - image's horizontal (x-axis) global lower bound of the part of the image being processed.
# minSize - The minimum area of the ractangle surrounding the object. Objects smaller than this are not considered valid.
# cancellationToken - A token that signals the parallel threads whether the object has been already found.
# target - the object into which the found coordinates will be inserted.
# threadID - the ID by which the parallel threads will be identified. Can be any value.
def createImageProcessor(img, verticalLowerBound, horizontalLowerBound, minSize, cancellationToken, target, threadID):
    imgProc = ImageProcessor(img, verticalLowerBound, horizontalLowerBound, minSize, cancellationToken, target,
                             threadID)
    imgProc.findObjectCoordinates()


# If the mouse is clicked, update threshholds of the selected object
def onmouse(event, x, y, flags, params):  # Funktsioon, mis nupuvajutuse peale uuendab värviruumi piire
    if event == cv2.EVENT_LBUTTONUP:
        if selectedTarget is not None:
            selectedTarget.updateThresholds(hsv[y][x])

# Captures an image and returns the original frame and a filtered image.
# colorScheme - the filter to be applied
def capture(colorScheme):
    # Capture frame-by-frame
    ret, capturedFrame = cap.read()
    # Check whether the frame exists.
    if not ret:
        print("Cannot read the frame")
        return None, None

    img = cv2.cvtColor(capturedFrame, colorScheme)  # Pane pilt etteantud värviskeemi
    return capturedFrame, img


# Blurs the image to remove noise
def blur(img):
    kernel = np.ones((50, 50), np.uint8)  # //TODO: Find values to put in the kernel
    closing = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
    gauss = cv2.GaussianBlur(img, (5, 5), 0)
    return gauss


# Finds object coordinates in the given picture
# img - the mask from which to find the coordinates
# verticalLowerBound - the image global vertical lower bound
# horizontalLowerbound - the image global horizontal lower bound
def findObject(img, verticalLowerBound, horizontalLowerBound, obj):
    obj.resetBounds()
    c = CancellationToken()
    createImageProcessor(img, verticalLowerBound, horizontalLowerBound, 1, c, obj, "0")


# Divides the given image into parts recursively. Then feeds the found parts to multiple threads to be processed for
# object coordinates.
# mainImg - The main frame. TODO: REMOVE IF NOT USED ANYMORE
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
def findObjectMultithreaded(mainImg, img, verticalLowerBound, verticalUpperBound, horizontalLowerBound,
                            horizontalUpperBound, minObjectSize, minImgArea, scanOrder, obj):
    obj.resetBounds()
    # print("*")

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
            findObjectMultithreaded(mainImg, img, verticalLowerBounds[scanOrder[i]],
                                                                       verticalUpperBounds[scanOrder[i]],
                                                                       horizontalLowerBounds[scanOrder[i]],
                                                                       horizontalUpperBounds[scanOrder[i]],
                                                                       minObjectSize * 3, minImgArea, scanOrder, obj)

            horizontalBounds, verticalBounds = obj.getBounds()
            # If an object was found by the called recursion, return its coordinates
            if horizontalBounds is not None and verticalBounds is not None:
                return

    # Create an object and a cancellation token for image processor
    cToken = CancellationToken()

    # Send each part of the image to a separate thread in the order specified by the caller of the funtion
    for i in range(len(scanOrder)):
        # print(i)

        # If an object has been found, return its coordinates
        if horizontalBounds is not None and verticalBounds is not None:
            return
        t = threading.Thread(target=createImageProcessor(img[
                                                         verticalLowerBounds[scanOrder[i]]:
                                                         verticalUpperBounds[scanOrder[i]],
                                                         horizontalLowerBounds[scanOrder[i]]:
                                                         horizontalUpperBounds[scanOrder[i]]
                                                         ],
                                                         verticalLowerBounds[scanOrder[i]],
                                                         horizontalLowerBounds[scanOrder[i]],
                                                         minObjectSize, cToken, obj, i))
        t.start()


# Finds the boundary coordinates of an object starting from a given pixel coordinates
# img - the image from which to look for the coordinates
# horizontalBounds - the array where horizontal coordinates are saved
# verticalBounds - the array where vertical coordinates are saved
# verticalCoordinate - the starting vertical coordinate
# horizontalCoordinate - the starting horizontal coordinate
# TODO: figure out whether the function will be used
def findBounds(img, height, width, horizontalBounds, verticalBounds, verticalCoordinate, horizontalCoordinate):
    # The given vertical coordinate is expected to be the bottom most coordinate of the object
    k = verticalCoordinate
    while (img[k][horizontalCoordinate] != 0 and k != 0):
        k -= 1
    verticalBounds[0] = k
    # Iterate through coordinates starting from the bottom coordinate until a black pixel is found
    # or the edge of the image is reached.
    for k in range(verticalCoordinate, height):
        # Black pixel found or image edge reached, this is the upper vertical coordinate of the object
        if img[k][horizontalCoordinate] == 0 or k == height - 1:
            verticalBounds[1] = k
            break

    # The object is expected to be symmetrical from vertical axis so the height of the object
    # is divided by 2 to find the midpoint. From the midpoint pixels are scanned from both sides of the point
    # if a black pixel or image edge is reached.
    midpoint = verticalBounds[0] + (verticalBounds[1] - verticalBounds[0]) // 2
    k = horizontalCoordinate
    while (img[midpoint][k] != 0 and k != 0):
        k -= 1
    horizontalBounds[0] = k
    k = horizontalCoordinate
    while (img[midpoint][k] != 0 and k != width - 1):
        k += 1
    horizontalBounds[1] = k

# Wrapper function to find coordinates of a given object
# mainImg - the main frame which is showed in the main window
# object - the mask from which the coordinates are to be detected
# objectMinSize - the minimum size of the blob starting from which it's considered valid
# imageMinArea - while the area of the part of the image being processed is bigger than this value, the image will be
# divided recursively by the multi threaded function. If not specified or less then 0, no no recursive calls shall be done.
# scanOrder - the order by which the image is fed to threads by multi threaded object finding function. More information
# in findObjectMultithreaded() description.
def detect(mainImg, target, objectMinSize, imageMinArea, scanOrder, obj):
    height, width = target.shape
    horizontalBounds = None
    verticalBounds = None

    if imageMinArea < 1:
        imageMinArea = height * width + 1

    if multiThreading:
        findObjectMultithreaded(mainImg, target, 0, height, 0, width, objectMinSize,
                                                                   imageMinArea, scanOrder, obj)
    else:
        findObject(target, 0, 0, obj)

cv2.namedWindow('main')
cv2.namedWindow('ball_filtered')
cv2.namedWindow('gate_filtered')
cv2.setMouseCallback('main', onmouse)

ball = Target(None, None, "ball")
basket = Target(None, None, "basket")
selectedTarget = ball
mb = MBcomm(mbLocation, 115200)
#mb = None
move = MovementLogic(mb)

while True:
    #move.drive(100)
    dt = datetime.now()
    #dt.microsecond
    start = float(str(dt).split()[1].split(":")[2]) * 1000000
    frame, hsv = capture(cv2.COLOR_BGR2HSV)  # Võta kaamerast pilt
    if frame is None:  # Kontroll, kas pilt on olemas
        print("Capture fucntion failed")
        break

    #hsv = blur(hsv)
    ballMask = cv2.inRange(hsv, ball.hsvLowerRange, ball.hsvUpperRange)  # Filtreeri välja soovitava värviga objekt
    ballMask = blur(ballMask)
    basketMask = cv2.inRange(hsv, basket.hsvLowerRange, basket.hsvUpperRange)
    basketMask = blur(basketMask)
    detect(frame, ballMask, 1000, 0, [1, 0, 2, 4, 3, 5, 7, 6, 8], ball)
    detect(frame, basketMask, 1000, 0, [7, 6, 8, 4, 3, 5, 1, 0, 2], basket)

    if ball.horizontalBounds is not None and ball.verticalBounds is not None:
        cv2.rectangle(frame, (ball.horizontalBounds[0], ball.verticalBounds[1]), (ball.horizontalBounds[1],
                                                                                ball.verticalBounds[0]), (255, 0, 0), 3)
    if basket.horizontalBounds is not None and basket.verticalBounds is not None:
        cv2.rectangle(frame, (basket.horizontalBounds[0], basket.verticalBounds[1]), (basket.horizontalBounds[1],
                                                                                        basket.verticalBounds[0]), (0, 255, 0), 3)

    if cv2.waitKey(1) & 0xFF == ord('e'):
        #        time.sleep(1)
        keyStroke = cv2.waitKey(100)
        if keyStroke & 0xFF == ord('q'):  # Nupu 'q' vajutuse peale välju programmist
            break
        #        time.sleep(1)
        if keyStroke & 0xFF == ord('b'):
            textColor = (0, 0, 255)
            selectedTarget = ball
            ball.resetThreshHolds()
            ball.resetBounds()

        #        time.sleep(1)
        if keyStroke & 0xFF == ord('k'):
            textColor = (255, 255, 0)
            selectedTarget = basket
            basket.resetThreshHolds()
            basket.resetBounds()

        if keyStroke & 0xFF == ord('m'):
            manual = ManualDrive(move)
            manual.run()

    # print("Object size: " + str((ballHorizontalBounds[1] - ballHorizontalBounds[0]) * (ballVerticalBounds[1] - ballVerticalBounds[0])))
    cv2.putText(frame, "FPS: " + str(fps), (30, 30), cv2.FONT_HERSHEY_SIMPLEX,
                1, textColor, 1)

    # Display the resulting frame
    cv2.imshow('ball_filtered', ballMask)
    cv2.imshow('main', frame)
    cv2.imshow('gate_filtered', basketMask)

    dt = datetime.now()
    #dt.microsecond
    stop = float(str(dt).split()[1].split(":")[2]) * 1000000
    framesCaptured += 1
    totalTimeElapsed += stop - start
    if framesCaptured >= 60:
        fps = (round(framesCaptured / (totalTimeElapsed / 1000000), 0))
        framesCaptured = 0
        totalTimeElapsed = 0

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
