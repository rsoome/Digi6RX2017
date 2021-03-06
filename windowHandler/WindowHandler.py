import threading

import cv2
#from manualDrive import ManualDrive
import sys
import re
import numpy as np


class WindowHandler:

    def __init__(self, socketData, socketHandler):
        self.socketHandler = socketHandler
        self.socketData = socketData
        cv2.namedWindow('main')
        cv2.setMouseCallback('main', self.onmouse)
        self.fps = "0"
        self.textColor = (0, 0, 255)
        self.values = dict()
        self.lock = threading.Lock()
        self.updateThresholds = False
        self.mouseX = -1
        self.mouseY = -1
        self.keyWaitTime = 200

    # If the mouse is clicked, update threshholds of the selected object
    def onmouse(self, event, x, y, flags, params):  # Funktsioon, mis nupuvajutuse peale uuendab värviruumi piire
        self.lock.acquire()
        if event == cv2.EVENT_LBUTTONUP:
            self.updateThresholds = True
            self.mouseX = x
            self.mouseY = y
            print("X: ", self.mouseX, "Y: ", self.mouseY)
        self.lock.release()

    def showImage(self):
        if self.socketData.ballHorizontalBounds != None and self.socketData.ballVerticalBounds != None:
            cv2.rectangle(self.socketData.img, (self.socketData.ballHorizontalBounds[0],
                                                self.socketData.ballVerticalBounds[1]),
                          (self.socketData.ballHorizontalBounds[1], self.socketData.ballVerticalBounds[0]),
                          (255, 0, 0), 3)

        if self.socketData.basketHorizontalBounds != None and self.socketData.basketVerticalBounds != None:
            cv2.rectangle(self.socketData.img, (self.socketData.basketHorizontalBounds[0],
                                                self.socketData.basketVerticalBounds[1]),
                          (self.socketData.basketHorizontalBounds[1], self.socketData.basketVerticalBounds[0]),
                          (0, 255, 0), 3)

        if cv2.waitKey(1) & 0xFF == ord('e'):
            #        time.sleep(1)
            self.values ={}
            keyStroke = cv2.waitKey(self.keyWaitTime)
            if keyStroke & 0xFF == ord('q'):  # Nupu 'q' vajutuse peale välju programmist
                self.values["stop"] = True
                self.values["gameStarted"] = False
                self.socketHandler.sendMessage(self.values, self.socketHandler.clientSock, 10)
                self.socketHandler.waitForAck(self.socketHandler.clientSock)
                self.closeWindows()
                self.socketData.stop = True
                return

            if keyStroke & 0xFF == ord('u'):
                self.values["updateThresholds"] = self.updateThresholds
                self.values["mouseX"] = self.mouseX
                self.values["mouseY"] = self.mouseY

            if keyStroke & 0xFF == ord('b'):
                self.textColor = (0, 0, 255)
                self.values["ballSelected"] = True
                if cv2.waitKey(self.keyWaitTime) == ord('b'):
                    self.values["resetBall"] = True

            if keyStroke & 0xFF == ord('k'):
                self.textColor = (255, 255, 0)
                self.values["basketSelected"] = True
                keyStroke = cv2.waitKey(self.keyWaitTime)
                if keyStroke == ord('k'):
                    self.values["resetBasket"] = True
                if keyStroke == ord('m'):
                    self.values["setMagneta"] = True
                if keyStroke == ord('b'):
                    self.values["setBlue"] = True

            if keyStroke & 0xFF == ord('m'):
                self.values["manualDrive"] = True

            if keyStroke & 0xFF == ord('g'):
                self.socketData.gameStarted = not self.socketData.gameStarted
                print("Setting game started to: " + str(self.socketData.gameStarted))
                self.values["gameStarted"] = self.socketData.gameStarted

            if keyStroke & 0xFF == ord('r'):
                self.values["refreshConf"] = True

            if keyStroke & 0xFF == ord('c'):
                self.values["updateConf"] = True

            if keyStroke & 0xFF == ord('d'):
                self.values["DC"] = True
                self.closeWindows()
                self.socketData.stop = True
                return

            self.socketHandler.sendMessage(self.values, self.socketHandler.clientSock, 1)

        frame = None

        if self.socketData.img is not None:
            #print("--------")
            #print(self.socketData.img)
            frame = self.socketData.img

        if frame is None:
            frame = np.zeros((480, 640, 3), np.uint8)

        cv2.putText(frame, "FPS: " + str(self.fps), (30, 30), cv2.FONT_HERSHEY_SIMPLEX,
                    1, self.textColor, 1)


        # Display the resulting frame
        cv2.imshow('main', frame)

    def createImageFromString(self, imgAsString):
        print(imgAsString)
        #imgDimensions = imgAsString.split("##")
        #print(imgDimensions[1])
        #dimensions = imgDimensions[0][1:len(imgDimensions[0])-1].split(", ")
        frame = imgAsString
        return frame

    def closeWindows(self):
        cv2.destroyAllWindows()
        self.socketData.stop = True
