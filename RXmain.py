# coding=utf-8

import cv2
import sys

import time

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
    print("Closing connections and writing new values to conf.")
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
        game.emptyThrower()
        mb.closeSerial()

    except Exception as e:
        print(e)

    try:
        frameCapture.releaseCapture()
    except Exception as e:
        print(e)

print("Running on Python " + sys.version)

settings = SettingsHandler.SettingsHandler("conf")

opponent = settings.getValue("opponentBasket")

if opponent != "magneta" and opponent != "blue":
    print("Please choose opponent basket color in conf (magneta/blue)")
    settings.writeFromDictToFile()
    sys.exit(0)

ball = Target.Target(None, None, "ball", settings.getValue("ballHSVLower"), settings.getValue("ballHSVUpper"),
                     settings.getValue("ballScanOrder"), settings.getValue("objectMInSize"))

basket = Target.Target(None, None, "basket", settings.getValue(opponent + "BasketHSVLower"),
                       settings.getValue(opponent + "BasketHSVUpper"),
                       settings.getValue("basketScanOrder"), settings.getValue("objectMinSize"))

blackLine = Target.Target(None, None, "blackLine", settings.getValue("blackLineHSVLower"),
                          settings.getValue("blackLineHSVUpper"),
                          settings.getValue("lineScanOrder"), settings.getValue("objectMinSize"))

robotID = settings.getValue("ID")
fieldID = settings.getValue("fieldID")

hsv = None

socketData = SocketData.SocketData()

mb = MBcomm.MBcomm(settings.getValue("mbLocation"), 115200)
#mb = None

move = MovementLogic.MovementLogic(mb)

frameCapture = FrameCapturer.FrameCapturer(int(settings.getValue("camID")))

imgHandler = ImageHandler.ImageHandler(bool(settings.getValue("multiThreading")), frameCapture,
                                       [ball, basket, blackLine], settings.getValue("minImgArea"))

ref = RefereeHandler.RefereeHandler(robotID, fieldID, mb)

game = GameLogic.GameLogic(move, settings.getValue("deltaFromMidPoint"), settings.getValue("driveSpeed"),
                           settings.getValue("turnSpeed"), frameCapture, socketData, ref, fieldID, robotID, mb, ball,
                           basket, settings.getValue("defaultGameState"))

socketHandler = SocketHandler.SocketHandler(socketData, ball, basket, 0, frameCapture)

timer = Timer.Timer()

t = threading.Thread(target=socketHandler.initServ)
t.start()

imgHandlerThread = threading.Thread(target=imgHandler.run())
imgHandlerThread.start()


def updateTargetsTresholds():
    print("Updating " + str(selectedTarget.id) + "'s thresholds.")
    for frameX in range(socketData.mouseX - 5, socketData.mouseX):
        for frameY in range(socketData.mouseY - 5, socketData.mouseY):
            if frameY != -1 and frameX != -1:
                ranges = selectedTarget.updateThresholds(frameCapture.filteredImg[frameY][frameX])
    print("New lower values: " + str(selectedTarget.hsvLowerRange))
    print("New upper values: " + str(selectedTarget.hsvUpperRange))
    settings.setValue(selectedTarget.id + "HSVLower", selectedTarget.hsvLowerRange.tolist())
    settings.setValue(selectedTarget.id + "HSVUpper", selectedTarget.hsvUpperRange.tolist())
    socketData.updateThresholds = False
    socketData.mouseX = -1
    socketData.mouseY = -1


def socketDataCheck():
    global selectedTarget, manualDrive, opponent, robotID, fieldID
    if socketData.updateThresholds:
        selectedTarget = None
        if socketData.ballSelected:
            selectedTarget = ball
        else:
            selectedTarget = basket

        updateTargetsTresholds()
    if socketData.resetBall:
        ball.resetBounds()
        ball.resetThreshHolds()
        socketData.resetBall = False
    if socketData.resetBasket:
        basket.resetBounds()
        basket.resetThreshHolds()
        socketData.resetBasket = False
    if socketData.manualDrive:
        manualDrive = ManualDrive.ManualDrive(move, int(settings.getValue("driveSpeed")),
                                              int(settings.getValue("turnSpeed")))
        manualDrive.run()
        socketData.manualDrive = False
    if socketData.gameStarted:
        print("Game mode activated")
        game.run()
        socketData.gameStarted = False
        print("Game mode deactivated")
        game.emptyThrower()
    if socketData.updateConf:
        print("Updating conf.")
        settings.writeFromDictToFile()
        socketData.updateConf = False
    if socketData.refreshConf:
        print("Refreshing conf")
        settings.values = settings.readFromFileToDict()
        opponent = settings.getValue("opponentBasket")
        robotID = settings.getValue("ID")
        fieldID = settings.getValue("fieldID")
        basket.setThresholds(settings.getValue(opponent + "BasketHSVLower"),
                             settings.getValue(opponent + "BasketHSVUpper"))
        ref.setIDs(robotID, fieldID)
        socketData.refreshConf = False


try:
    mb.sendTimer.startTimer()
    while True:

        #DEBUGGING LOOKING FOR TARGET
        #game.lookForTarget(ball)
        #END DEBUGGING


        mb.setGrabberPosition(mb.GRABBER_OPEN_POSITION)

        if mb.sendingTime():
            mb.sendValues()

        timer.startTimer()

        game.readMb()
        if frameCapture.capturedFrame is not None:
            frameCapture.capture(cv2.COLOR_BGR2HSV)  # Võta kaamerast pilt
            frame = frameCapture.capturedFrame

            if frame is None:  # Kontroll, kas pilt on olemas
                socketData.stop = True
                while not socketData.socketClosed:
                    pass
                print("Capture fucntion failed")
                break

        socketDataCheck()

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
