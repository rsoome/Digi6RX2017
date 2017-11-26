import cv2
import time

import math

from timer import Timer
# Contins the game logic
# TODO: Implement
class GameLogic:

    def __init__(self, move, deltaFromMidPoint, moveSpeed, turnSpeed, frame, socketData, ref, fieldID, robotID, mb,
                 ball, basket, defaultGameState, thrower):
        self.frameWidth = None
        self.move = move
        self.deltaFromMidPoint = deltaFromMidPoint
        self.moveSpeed = moveSpeed
        self.turnSpeed = turnSpeed
        self.frame = frame
        self.initializeValues()
        self.socketData = socketData
        self.thrower = thrower
        self.ballStopBound = 330
        self.basketStopBound = 0
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
        self.basketAheadBound = 70

    def turnTowardTarget(self, target):
        horizontalMidPoint = target.horizontalMidPoint
        if horizontalMidPoint == None:
            return False
        turnCoificent = (horizontalMidPoint - self.screenMidpoint)/self.screenMidpoint

        print("Turncoificent: " + str(turnCoificent))
        if not self.socketData.gameStarted:
            return False
        turningSpeed = self.turnSpeed * turnCoificent
        print("Turning with speed: " + str(turningSpeed))
        self.move.rotate(turningSpeed)
        return True

    def moveTowardTarget(self, target):
        horizontalMidPoint = target.horizontalMidPoint
        verticalMidPoint = target.verticalMidPoint
        if horizontalMidPoint is None:
            return

        if verticalMidPoint is None:
            return

        if not self.socketData.gameStarted:
            return

        print("Verticalmidpoint: " + str(target.verticalMidPoint))
        print("target midpoint: ", target.horizontalMidPoint)
        print("screen midpoint: ", self.screenMidpoint)
        ySpeed = self.move.calculateSpeed(self.moveSpeed, verticalMidPoint)
        turnSpeed = self.move.calculateOmega(self.turnSpeed, horizontalMidPoint - self.screenMidpoint)
        #if abs(turnSpeed) < 0.2:
         #   turnSpeed = 0
        print("ySpeed: ",ySpeed)
        print("turnSpeed: ", turnSpeed)
        self.move.driveXY(0, ySpeed, turnSpeed)

    def lookForTarget(self, target):

        #print(target.horizontalMidPoint)
        self.move.rotate(self.turnSpeed)
        if self.mb.sendingTime:
            self.mb.sendValues()

        if target.horizontalMidPoint is not None:
            return True

        return False

    def run(self):
        ballReached = False
        basketReached = False
        ballGrabbed = False
        self.mb.sendTimer.startTimer()
        self.thrower.grabberOpen()
        self.thrower.stopMotor()

        while self.socketData.gameStarted:
            self.readMb()
            #print(self.irStatus)

            if self.mb.sendingTime():
                self.mb.sendValues()

            if self.gameState == "START":

                if self.irStatus == 1 and not ballGrabbed:
                    #self.move.driveXY(0, self.move.currentSpeed, 0) #MAY NEED CHANGING
                    time.sleep(0.1)
                    self.readMb()
                    self.thrower.startMotor()
                    if self.irStatus == 1:
                        print("Grabbing ball")
                        self.thrower.grabberCarry()
                        self.mb.sendValues()
                        time.sleep(0.05)
                        if self.basket.verticalBounds is not None:
                            while self.basket.getDistance() < 30:
                                self.move.driveXY(0, -self.move.currentSpeed, 0)
                                if self.mb.sendTime():
                                    self.mb.sendValues()
                        self.mb.sendValues()
                        ballReached = True
                        ballGrabbed = True

                elif not ballGrabbed:
                    self.readMb()
                    if self.irStatus == 0:
                        self.thrower.grabberOpen()
                        self.thrower.stopMotor()
                        ballReached = False
                        ballGrabbed = False

                if not ballReached:
                    print("Going to ball")
                    print(self.ball.horizontalMidPoint)
                    self.thrower.grabberOpen()
                    ballReached = self.goToTarget(self.ball, self.ballStopBound, self.moveSpeed)
                    if ballReached:
                        self.move.driveXY(0, self.move.currentSpeed, 0)
                        self.mb.sendValues()

                elif not ballGrabbed:
                    ballReached = self.checkVerticalAlignment(self.ball, self.ballStopBound) and self.checkHorizontalAlginment(self.ball)
                    if ballReached:
                        print("Getting ball")
                        ballGrabbed = self.irStatus == 1
                        self.move.driveXY(0, self.move.currentSpeed, 0)
                        self.mb.sendValues()
                        if not ballGrabbed:
                            time.sleep(0.1)

                        if ballGrabbed:
                            self.thrower.grabberCarry()
                            self.mb.sendValues()
                            time.sleep(0.05)
                            self.thrower.startMotor()
                        else:
                            self.thrower.grabberOpen()
                            self.thrower.stopMotor()
                        self.mb.sendValues()
                    else:
                        self.move.stop()
                        ballReached = False

                elif not basketReached:
                    print("Reaching basket")
                    basketReached = self.goToTarget(self.basket, self.basketStopBound, self.moveSpeed)

                elif (self.irStatus == 1):
                    print("Throwing ball")
                    basketReached = self.throwBall(self.basket.getDistance())
                    if basketReached:
                        ballReached = (self.irStatus == 1)
                        ballGrabbed = ballReached
                        if ballGrabbed:
                            self.thrower.grabberCarry()
                        ballReached = False
                        basketReached = False
                        ballGrabbed = False

                else:
                    ballReached = False
                    basketReached = False
                    ballGrabbed = False

            if self.gameState == "STOP":
                self.thrower.emptyThrower()
                self.move.stop()

        self.mb.sendTimer.stopTimer()
        self.move.stop()

    def goToTarget(self, target, verticalStopBound, speed):
        #print(target.area)
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

                basketHorizontalMidPoint = self.basket.horizontalMidPoint

                if basketHorizontalMidPoint is not None:

                    driveTimer = Timer.Timer()
                    driveTimer.startTimer()

                    while driveTimer.getTimePassed() < 1000:
                        self.move.driveXY(0, self.move.currentSpeed, 0)
                        self.mb.sendValues()

                        if target.horizontalMidPoint is not None:
                            return True

                        if self.basket.verticalBounds is None or self.basket.verticalBounds[1] >= self.basketAheadBound:
                            self.move.rotate(self.turnSpeed)
                            return False

                        time.sleep(0.05)
                    driveTimer.stopTimer()

                return False
            else:
                self.move.stop()
                self.mb.sendValues()

        elif not self.checkVerticalAlignment(target, verticalStopBound):
            print("Alligning Vertically")
            self.moveTowardTarget(target)
            self.mb.sendValues()
            return False

        elif not self.checkHorizontalAlginment(target):
            print("Alligning horizontally.")
            self.turnTowardTarget(target)
            self.mb.sendValues()
            return False

        print("At position.")
        self.move.stop()
        self.mb.sendValues()
        return True

    def initializeValues(self):
        self.frame.capture(cv2.COLOR_BGR2HSV)
        self.screenMidpoint = self.frame.width//2

    def checkHorizontalAlginment(self, target):

        horizontalMidPoint = target.horizontalMidPoint
        if horizontalMidPoint is None:
            return False

        if (horizontalMidPoint < (self.screenMidpoint - self.deltaFromMidPoint)
            or horizontalMidPoint > (self.screenMidpoint + self.deltaFromMidPoint)):

            print("Target not in allowed bounds: ")

            return False

        return True

    def checkVerticalAlignment(self, target, verticalStopBound):

        verticalMidPoint = target.verticalMidPoint
        print(target.id, "'s vertical midpoint at the time of checking allignment: ", verticalMidPoint)
        if verticalMidPoint is None:
            return False

        if verticalMidPoint < verticalStopBound:
            return False
        print("Vertically alligned.")
        self.move.stop()
        self.mb.sendValues()
        return True

    def handleMbMessage(self, msg):
        print("Message from mainboard: " + str(msg))
        if msg != None:
            sendingNode = msg[0]

            if sendingNode == "motors":
                self.move.motorSpeed0 = float(msg[1])
                self.move.motorSpeed1 = float(msg[2])
                self.move.motorSpeed2 = float(msg[3])

            if sendingNode == "ir":
                try:
                    self.irStatus = int(msg[1])
                except:
                    pass
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

    def throwBall(self,distance):
        if not self.checkHorizontalAlginment(self.basket) or not self.checkVerticalAlignment(self.basket, self.basketStopBound):
            return False

        self.thrower.throw(distance)
        print("throwing irStatus " + str(self.irStatus))
        return True
