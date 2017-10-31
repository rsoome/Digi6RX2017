# coding=utf-8

import numpy as np
import cv2
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
from refereeHandler import RefereeHandler
from timer import Timer

def closeConnections():
    settings.writeFromDictToFile()
    try:
        socketHandler.servSock.close()
    except Exception as e:
        print(e)

    try:
        socketHandler.clientSock.close()
    except Exception as e:
        print(e)

    try:
        mb.ser.close()
    except Exception as e:
        print(e)

    try:
        frameCapture.releaseCapture()
    except Exception as e:
        print(e)

    mb.closeSerial()

print("Running on Python " + sys.version)

settings = SettingsHandler.SettingsHandler("conf")

ball = Target.Target(None, None, "ball", np.array([int(x) for x in settings.getValue("ballHSVLower").split()]),
                     np.array([int(x) for x in settings.getValue("ballHSVUpper").split()]),
                     [int(x) for x in settings.getValue("ballScanOrder").split()])

basket = Target.Target(None, None, "basket", np.array([int(x) for x in settings.getValue("basketHSVLower").split()]),
                       np.array([int(x) for x in settings.getValue("basketHSVUpper").split()]),
                       [int(x) for x in settings.getValue("basketScanOrder").split()])

robotID = settings.getValue("ID")
fieldID = settings.getValue("fieldID")

hsv = None

socketData = SocketData.SocketData()

mb = MBcomm.MBcomm(settings.getValue("mbLocation"), 115200)

move = MovementLogic.MovementLogic(mb)

imgHandler = ImageHandler.ImageHandler(bool(settings.getValue("multiThreading")))

frameCapture = FrameCapturer.FrameCapturer(int(settings.getValue("camID")))

ref = RefereeHandler.RefereeHandler(robotID, fieldID, mb)

game = GameLogic.GameLogic(move, 40, int(settings.getValue("driveSpeed")), int(settings.getValue("turnSpeed")),
                           imgHandler, frameCapture, socketData, ref, fieldID, robotID, mb, ball, basket,
                           settings.getValue("defaultGameState"))

socketHandler = SocketHandler.SocketHandler(socketData, ball, basket, 0, frameCapture)

timer = Timer.Timer()

t = threading.Thread(target=socketHandler.initServ)
t.start()
try:
    while True:

        timer.startTimer()

        game.readMb()
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
            print("Game mode deactivated")

        if socketData.stop:
            break

        game.addFrame(timer.stopTimer())

        game.updateFPS()

        socketHandler.updateData()

    print("Exit.")
    closeConnections()

except KeyboardInterrupt:
    print("Canceled by user with keyboard interrupt")

    closeConnections()

except Exception as e:

    closeConnections()

    raise e
