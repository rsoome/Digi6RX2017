import cv2
import time

from timer import Timer
# Contins the game logic
# TODO: Implement
class GameLogic:

    def __init__(self, move, deltaFromMidPoint, moveSpeed, turnSpeed, imgHandler, frame, socketData, ref, fieldID,
                 robotID, mb, ball, basket, defaultGameState):
        self.screenMidpoint = None
        self.move = move
        self.deltaFromMidPoint = deltaFromMidPoint
        self.moveSpeed = moveSpeed
        self.turnSpeed = turnSpeed
        self.imgHandler = imgHandler
        self.frame = frame
        self.initializeValues()
        self.socketData = socketData
        self.ballVerticalStopBound = 400
        self.basketVerticalStopBound = 240
        self.gameState = defaultGameState
        self.irStatus = -1.0
        self.ref = ref
        self.fieldID = fieldID
        self.robotID = robotID
        self.mb = mb
        self.ball = ball
        self.basket = basket
        self.framesCaptured = 0
        self.totalTimeElapsed = 0
        self.fps = 0
        self.timer = Timer.Timer()

    def turnTowardTarget(self, target):
        if target.horizontalMidPoint is not None:
            if not self.socketData.gameStarted:
                return
            if target.horizontalMidPoint > self.screenMidpoint + self.deltaFromMidPoint:
                self.move.rotate(self.turnSpeed, 1)
            elif target.horizontalMidPoint < self.screenMidpoint - self.deltaFromMidPoint:
                self.move.rotate(-self.turnSpeed, 1)

    def moveTowardTarget(self, target):
        if target.horizontalMidPoint is not None:

            if target.verticalMidPoint is None:
                return

            if not self.socketData.gameStarted:
                return
            self.move.drive(self.moveSpeed, 0)

    def updateTargetCoordinates(self, targets):
        self.frame.capture(cv2.COLOR_BGR2HSV)
        for target in targets:
            self.imgHandler.generateMask(target, self.frame.filteredImg)
            self.imgHandler.detect(None, target.mask, 1000, 0, target.scanOrder, target)

    def lookForTarget(self, target):
        if not self.socketData.gameStarted:
            return False
        for i in range(12):
            self.updateTargetCoordinates([target])
            self.move.rotate(self.turnSpeed, 30)
            if target.horizontalMidPoint is not None:
                return True

        return False

    def run(self):
        ballReached = False
        basketReached = False
        while self.socketData.gameStarted:
            self.timer.startTimer()
            self.updateTargetCoordinates([self.ball, self.basket])
            self.readMb()
            if self.gameState == "START":

                if not ballReached:
                    ballReached = self.goToTarget(self.ball, self.ballVerticalStopBound)

                elif not basketReached:
                    self.move.stop()
                    basketReached = self.goToTarget(self.basket, self.basketVerticalStopBound)

                else:
                    self.move.stop()
                    ballThrown = self.throwBall()
                    ballReached = not ballThrown
                    basketReached = False

            if self.gameState == "STOP":
                self.move.stop()

            self.addFrame(self.timer.stopTimer())
            self.updateFPS()

        self.move.stop()

    def goToTarget(self, target, verticalStopBound):

        if target.verticalMidPoint == None or target.horizontalMidPoint == None:
            if not self.lookForTarget(target):
                time.sleep(0.01)
                print("Looking for " + target.id)
                for i in range(120):
                    print(i)
                    self.move.drive(self.moveSpeed, 0)
                return False

        if not self.checkHorizontalAlginment(target):
            self.turnTowardTarget(target)
            return False

        elif not self.checkVerticalAlignment(target, verticalStopBound):
            self.moveTowardTarget(target)
            return False

        return True

    def initializeValues(self):
        self.frame.capture(cv2.COLOR_BGR2HSV)
        self.screenMidpoint = self.frame.width//2

    def checkHorizontalAlginment(self, target):

        if target.horizontalMidPoint is None:
            return False

        if (target.horizontalMidPoint > (self.screenMidpoint + self.deltaFromMidPoint)
            or target.horizontalMidPoint < (self.screenMidpoint - self.deltaFromMidPoint)):

            return False

        return True

    def checkVerticalAlignment(self, target, verticalStopBound):

        if target.verticalMidPoint is None:
            return False

        if target.verticalMidPoint < verticalStopBound:
            return False

        return True

    def handleMbMessage(self, msg):
        print(msg)
        sendingNode = msg[0]

        if sendingNode == "motors":
            self.move.motorSpeed0 = float(msg[1])
            self.move.motorSpeed1 = float(msg[2])
            self.move.motorSpeed2 = float(msg[3])

        if sendingNode == "ir":
            self.irStatus = float(msg[1])

        if sendingNode == "ref":
            cmd = self.ref.handleCommand(msg[1])
            #print(cmd)

            if cmd == "START":
                self.gameState = "START"

            if cmd == "STOP":
                self.gameState = "STOP"

            if cmd == "PING":
                print("Sending ACK")

    def readMb(self):
        mbMsg = self.mb.readBytes()

        if len(mbMsg) > 0:
            self.handleMbMessage(mbMsg)

    def throwBall(self):
        if not self.checkHorizontalAlginment(self.basket) or not self.checkVerticalAlignment(self.basket, self.basketVerticalStopBound):
            return False
        self.mb.startThrower(self.mb.THROWER_MAXSPEED)
        return True

    def addFrame(self, elapsed):
        if elapsed > 0:
            self.framesCaptured += 1
            self.totalTimeElapsed += elapsed

    def updateFPS(self):
        if self.framesCaptured >= 60:
            self.fps = (round(self.framesCaptured / (self.totalTimeElapsed / 1000000), 0))
            self.framesCaptured = 0
            self.totalTimeElapsed = 0

        self.socketData.fps = self.fps