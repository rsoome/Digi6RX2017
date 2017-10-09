# coding=utf-8

import numpy as np
import cv2
from datetime import datetime
import sys
from settings import SettingsHandler
from target import Target
from  movementLogic import MovementLogic
from imageProcessor import ImageHandler
from imageProcessor import FrameCapturer
from manualDrive import ManualDrive
from windowHandler import WindowHandler
from mbcomm import MBcomm

print("Running on Python " + sys.version)

settings = SettingsHandler.SettingsHandler("conf")

textColor = (0, 0, 255)

framesCaptured = 0
totalTimeElapsed = 0
fps = 0

ball = Target.Target(None, None, "ball",
              np.array([int(x) for x in settings.getValue("ballHSVLower").split()]),
              np.array([int(x) for x in settings.getValue("ballHSVUpper").split()]))
basket = Target.Target(None, None, "basket",
              np.array([int(x) for x in settings.getValue("basketHSVLower").split()]),
              np.array([int(x) for x in settings.getValue("basketHSVUpper").split()]))

hsv = None

mb = MBcomm.MBcomm(settings.getValue("mbLocation"), 115200)
#mb = None
move = MovementLogic.MovementLogic(mb)
imgHandler = ImageHandler.ImageHandler(bool(settings.getValue("multiThreading")))
frameCapture = FrameCapturer.FrameCapturer(int(settings.getValue("camID")))
window = WindowHandler.WindowHandler(frameCapture, ball, basket, int(settings.getValue("driveSpeed")),
                                     int(settings.getValue("turnSpeed")), move)

#screen = curses.initscr()
#curses.cbreak()
#screen.keypad(1)

keyStroke = ''
#keyStroke = screen.getch()
while True:
    dt = datetime.now()
    #dt.microsecond
    start = float(str(dt).split()[1].split(":")[2]) * 1000000
    frameCapture.capture(cv2.COLOR_BGR2HSV)  # Võta kaamerast pilt
    frame = frameCapture.capturedFrame
    hsv = frameCapture.filteredImg
    if frame is None:  # Kontroll, kas pilt on olemas
        print("Capture fucntion failed")
        break

    #hsv = blur(hsv)
    imgHandler.generateMask(ball, hsv)
    imgHandler.generateMask(basket, hsv)
    imgHandler.detect(frame, ball.mask, 1000, 0, [1, 0, 2, 4, 3, 5, 7, 6, 8], ball)
    imgHandler.detect(frame, basket.mask, 1000, 0, [7, 6, 8, 4, 3, 5, 1, 0, 2], basket)

    window.showImage()
    if window.halt:
        break

    dt = datetime.now()
    #dt.microsecond
    stop = float(str(dt).split()[1].split(":")[2]) * 1000000
    framesCaptured += 1
    totalTimeElapsed += stop - start
    if framesCaptured >= 60:
        fps = (round(framesCaptured / (totalTimeElapsed / 1000000), 0))
        framesCaptured = 0
        totalTimeElapsed = 0

settings.writeFromDictToFile()
frameCapture.releaseCapture()
