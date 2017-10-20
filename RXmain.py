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
from mbcomm import MBcomm
from gameLogic import GameLogic
from socketHandler import SocketHandler
from socketHandler import SocketData
import threading
from manualDrive import ManualDrive

print("Running on Python " + sys.version)

settings = SettingsHandler.SettingsHandler("conf")

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

#mb = MBcomm.MBcomm(settings.getValue("mbLocation"), 115200)
mb = None
move = MovementLogic.MovementLogic(mb)
imgHandler = ImageHandler.ImageHandler(bool(settings.getValue("multiThreading")))
frameCapture = FrameCapturer.FrameCapturer(int(settings.getValue("camID")))
game = GameLogic.GameLogic(move, 0, int(settings.getValue("driveSpeed")),
                           int(settings.getValue("turnSpeed")), imgHandler, frameCapture)
socketData = SocketData.SocketData()
socketHandler = SocketHandler.SocketHandler(socketData, ball, basket, fps, frameCapture)
t = threading.Thread(target=socketHandler.initServ)
t.start()

while True:
    dt = datetime.now()
    #dt.microsecond
    start = float(str(dt).split()[1].split(":")[2]) * 1000000
    frameCapture.capture(cv2.COLOR_BGR2HSV)  # Võta kaamerast pilt
    frame = frameCapture.capturedFrame
    hsv = frameCapture.filteredImg

    if frame is None:  # Kontroll, kas pilt on olemas
        socketData.stop = True
        while not socketData.socketClosed:
            pass
        print("Capture fucntion failed")
        break

    imgHandler.generateMask(ball, hsv)
    imgHandler.generateMask(basket, hsv)
    imgHandler.detect(frame, ball.mask, int(settings.getValue("objectMinSize")), int(settings.getValue("minImgArea")),
                      [int(x) for x in settings.getValue("ballScanOrder").split()], ball)

    imgHandler.detect(frame, basket.mask, int(settings.getValue("objectMinSize")), int(settings.getValue("minImgArea")),
                      [int(x) for x in settings.getValue("basketScanOrder").split()], basket)

    if socketData.updateThresholds:
        selectedTarget = None
        if socketData.ballSelected:
            selectedTarget = ball
        else:
            selectedTarget = basket

        if socketData.mouseY != -1 and socketData.mouseX != -1:
            selectedTarget.updateThresholds(hsv[socketData.mouseY][socketData.mouseX])
        socketData.updateThresholds = False
        socketData.mouseX = -1
        socketData.mouseY = -1

    if socketData.resetBall:
        ball.resetBounds()
        ball.resetThreshHolds()
        socketData.resetBall = False

    if socketData.resetBasket:
        basket.resetBounds()
        basket.resetThreshHolds()
        socketData.resetBasket = False

    if socketData.manualDrive:
        manualDrive = ManualDrive.ManualDrive(move, int(settings.getValue("driveSpeed")), int(settings.getValue("turnSpeed")))
        manualDrive.run()
        socketData.manualDrive = False

    if socketData.gameStarted:
        print("Game mode activated")
        game.run()
        socketData.gameStarted = False

    if socketData.stop:
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

    socketData.fps = fps
    socketHandler.updateData()


settings.writeFromDictToFile()
frameCapture.releaseCapture()
