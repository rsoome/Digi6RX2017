import cv2
import time

from timer import Timer
# Contins the game logic
# TODO: Implement
class GameLogic:

    def __init__(self, move, deltaFromMidPoint, moveSpeed, turnSpeed, imgHandler, frame, socketData, ref, fieldID,
                 robotID, mb, ball, basket, defaultGameState):
        self.frameWidth = None
        self.move = move
        self.deltaFromMidPoint = deltaFromMidPoint
        self.moveSpeed = moveSpeed
        self.turnSpeed = turnSpeed
        self.imgHandler = imgHandler
        self.frame = frame
        self.initializeValues()
        self.socketData = socketData
        self.ballVerticalStopBound = self.frame.height - 20
        self.basketVerticalStopBound = 0
        self.gameState = defaultGameState
        self.irStatus = 0
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
        minTurnSpeed = 10
        turnCoificent = abs(target.horizontalMidPoint - self.screenMidpoint)/float(self.screenMidpoint)
        currentTurnSpeed = minTurnSpeed + turnCoificent*self.turnSpeed
        if target.horizontalMidPoint is not None:
            if not self.socketData.gameStarted:
                return
            self.moveTowardTarget(target)
            #if target.horizontalMidPoint > self.screenMidpoint + self.deltaFromMidPoint:
            #    self.move.rotate(currentTurnSpeed)
            #elif target.horizontalMidPoint < self.screenMidpoint - self.deltaFromMidPoint:
            #    self.move.rotate(-currentTurnSpeed)

    def moveTowardTarget(self, target):
        if target.horizontalMidPoint is not None:

            if target.verticalMidPoint is None:
                return

            if not self.socketData.gameStarted:
                return

            print("Verticalmidpoint: " + str(target.verticalMidPoint))
            print("Jagamine: " + str(1 - float(target.verticalMidPoint)/self.frame.height))
            print("moveSpeed" + str(self.moveSpeed))
            print("CalculateSpeed: " + str(self.move.calculateSpeed(self.moveSpeed, 1 - float(target.verticalMidPoint)/self.frame.height)))
            self.move.driveXY(0,

                              self.move.calculateSpeed(self.moveSpeed, 1 - float(target.verticalMidPoint)/self.frame.height),
                                0)
                              #self.move.calculateSpeed(self.moveSpeed,
                              #                         (target.horizontalMidPoint - self.screenMidpoint) / float(self.screenMidpoint))
                              #)

    def updateTargetCoordinates(self, targets):
        self.frame.capture(cv2.COLOR_BGR2HSV)
        for target in targets:
            self.imgHandler.detect(1000, 0, target.scanOrder, target)

    def lookForTarget(self, target):
        if not self.socketData.gameStarted:
            print("Game ended by client.")
            return False

        #print(target.horizontalMidPoint)
        self.move.rotate(self.turnSpeed)
        self.updateTargetCoordinates([target])
        if target.horizontalMidPoint is not None:
            return True

        return False

    def run(self):
        ballReached = False
        basketReached = False
        ballGrabbed = False

        while self.socketData.gameStarted:
            self.timer.startTimer()
            self.updateTargetCoordinates([self.ball, self.basket])
            self.readMb()

            if self.gameState == "START":

                if self.irStatus == 1:
                    ballReached = True
                else:
                    ballReached = False

                if not ballReached:
                    self.mb.setGrabberPosition(self.mb.GRABBER_OPEN_POSITION)
                    atPosition = self.goToTarget(self.ball, self.ballVerticalStopBound, self.moveSpeed)
                    if atPosition:
                        self.move.drive(int(self.moveSpeed), 0, 0)

                elif ballReached and not ballGrabbed:
                    #print("Reaching ball")
                    self.move.drive(int(self.moveSpeed), 0, 0)
                    time.sleep(0.1)
                    self.mb.setGrabberPosition(self.mb.GRABBER_CARRY_POSITION)
                    time.sleep(0.3)
                    ballGrabbed = True

                elif not basketReached:
                    self.move.stop()
                    basketReached = self.goToTarget(self.basket, self.basketVerticalStopBound, self.moveSpeed)

                elif (self.irStatus == 1):
                    throwTimer = Timer.Timer()
                    #print("Throwing ball")
                    self.move.stop()
                    ballThrown = self.throwBall()
                    time.sleep(0.1)
                    ballReached = (self.irStatus == 1)
                    ballGrabbed = ballReached
                    if ballGrabbed:
                        self.mb.setGrabberPosition(self.mb.GRABBER_CARRY_POSITION)
                    basketReached = False
                    throwTimer.startTimer()
                    while throwTimer.getTimePassed() < 1000:
                        self.handleMbMessage(self.mb.readInfrared())
                        time.sleep(0.1)
                    throwTimer.stopTimer()

            if self.gameState == "STOP":
                self.move.stop()

            self.addFrame(self.timer.stopTimer())
            self.updateFPS()

        self.move.stop()

    def goToTarget(self, target, verticalStopBound, speed):

        if target.verticalMidPoint == None or target.horizontalMidPoint == None:
            turnTimer = Timer.Timer()
            turnTimer.startTimer()
            targetFound = self.lookForTarget(target)
            while not targetFound:
                targetFound = self.lookForTarget(target)
                if turnTimer.getTimePassed() >= 1000:
                    break
            turnTimer.stopTimer()

            if not targetFound:
                print("Looking for " + target.id)
                for i in range(2000):
                    #print(i)
                    self.move.driveXY(0, self.moveSpeed, 0)
                    self.move.stop()
                return False

        if not self.checkHorizontalAlginment(target):
            self.move.stop()
            self.turnTowardTarget(target)
            return False

        elif not self.checkVerticalAlignment(target, verticalStopBound):
            self.moveTowardTarget(target)
            return False

        self.move.stop()
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
            self.irStatus = int(msg[1])
            print("irStatus: " + str(self.irStatus))

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
        self.mb.setThrowerSpeed(self.mb.THROWER_MIDSPEED)
        time.sleep(0.5)
        self.mb.setThrowerSpeed(self.mb.THROWER_MAXSPEED)
        time.sleep(0.5)
        self.mb.setGrabberPosition(self.mb.GRABBER_THROW_POSITION)
        time.sleep(0.5)
        self.mb.setThrowerSpeed(self.mb.THROWER_STOP)
        self.mb.setGrabberPosition(self.mb.GRABBER_OPEN_POSITION)
        print("throwing irStatus " + str(self.irStatus))
        return True

    def addFrame(self, elapsed):
        if elapsed > 0:
            self.framesCaptured += 1
            self.totalTimeElapsed += elapsed

    def updateFPS(self):
        if self.framesCaptured >= 60:
            self.fps = (round(self.framesCaptured / (self.totalTimeElapsed / 1000), 0))
            self.framesCaptured = 0
            self.totalTimeElapsed = 0

        self.socketData.fps = self.fps
