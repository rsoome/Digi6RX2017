import cv2
import time

import math

from timer import Timer
# Contins the game logic
# TODO: Implement
class GameLogic:

    def __init__(self, move, deltaFromMidPoint, moveSpeed, turnSpeed, frame, socketData, ref, fieldID, robotID, mb,
                 ball, basket, defaultGameState, thrower, blackLine):
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
        self.basketStopBound = 0.006
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
        self.basketAheadBound = self.frame.height + 70
        self.blackLine = blackLine
        self.lineAheadBound = self.frame.height + 70
        self.searchTimer = Timer.Timer()

    def turnTowardTarget(self, target):
        horizontalMidPoint = target.getHorizontalData()
        if horizontalMidPoint == None:
            return False
        turnCoificent = (horizontalMidPoint - self.screenMidpoint)/self.screenMidpoint

        #print("Turncoificent: " + str(turnCoificent))
        if not self.socketData.gameStarted:
            return False
        turningSpeed = turnCoificent
        #print("Turning with speed: " + str(turningSpeed))
        self.readMb()
        if target.id == "ball" and self.irStatus == 1:
            return True
        self.move.rotate(turningSpeed)
        self.mb.sendValues()
        return True

    def moveTowardTarget(self, target):
        horizontalMidPoint = target.getHorizontalData()
        verticalMidPoint = target.getVerticalData()
        if horizontalMidPoint is None:
            return

        if verticalMidPoint is None:
            return

        if not self.socketData.gameStarted:
            return

        ySpeed = self.move.calculateSpeed(self.moveSpeed, verticalMidPoint)
        turnSpeed = self.move.calculateOmega(self.turnSpeed, horizontalMidPoint)
        #print("Current speed: ", ySpeed)
        self.move.driveXY(0, ySpeed, turnSpeed)

    def lookForTarget(self, target):

        self.readMb()
        if target.id == "ball" and self.irStatus == 1:
            return True
        print("Looking for target")
        self.move.rotate(1)
        self.mb.sendValues()

        if target.getHorizontalData is not None:
            return True

        return False

    def run(self):
        ballReached = False
        basketReached = False
        ballGrabbed = False
        self.thrower.grabberOpen()
        self.thrower.stopMotor()
        grabbingTimer = Timer.Timer()
        effTimer = Timer.Timer()
        effTimer.startTimer()
        while self.socketData.gameStarted:
            self.readMb()
            #print(self.irStatus)

            self.mb.sendValues()

            if self.gameState == "START":

                self.checkBounds()

                if self.irStatus == 1:
                    self.thrower.startMotor()
                    if not ballGrabbed:
                        #self.move.driveXY(0,self.move.currentSpeed, 0)
                        self.thrower.startMotor()
                        self.thrower.grabberCarry()
                        self.mb.sendValues(wait=True)
                        time.sleep(0.05)
                        self.readMb()
                        grabbingTimer.stopTimer()
                        if self.irStatus == 1:
                            print("Ball caught")
                            distanceFromBasket = self.basket.getDistance()
                            if distanceFromBasket is not None:
                                while distanceFromBasket < 30:
                                    print("Getting further from the basket.")
                                    self.move.driveXY(0, -self.move.currentSpeed, 0)
                                    self.mb.sendValues(wait=True)
                                    distanceFromBasket = self.basket.getDistance()
                                    if distanceFromBasket is None:
                                        break

                            self.move.stop()
                            self.mb.sendValues(wait=True)
                            ballReached = True
                            ballGrabbed = True
                            basketReached = False

                elif self.irStatus == 0:
                    self.thrower.grabberOpen()
                    ballGrabbed = False

                if not ballGrabbed:
                    self.readMb()
                    if self.irStatus == 0:
                        self.thrower.grabberOpen()
                        self.thrower.stopMotor()
                        ballGrabbed = False

                if ballReached == False:
                    self.readMb()
                    if self.irStatus == 1:
                        ballReached = True
                    else:
                        print("Going to ball")
                        #print(self.ball.horizontalMidPoint)
                        self.thrower.grabberOpen()
                        ballReached = self.goToTarget(self.ball, self.ballStopBound)
                        if ballReached:
                            self.move.driveXY(0, 0.15, 0)

                elif ballGrabbed == False:
                    if not grabbingTimer.isStarted:
                        grabbingTimer.startTimer()

                    if grabbingTimer.getTimePassed() < 500:
                        print("Grabbing ball")
                        ballGrabbed = self.irStatus == 1
                        #self.move.driveXY(0, self.move.currentSpeed, 0)
                        #print("I should be driving with speed: ", self.move.currentSpeed)
                        #self.mb.sendValues()
                    else:
                        ballReached = False

                elif basketReached == False:
                    self.readMb()
                    if self.irStatus == 1:
                        print("Reaching basket")
                        basketReached = self.goToTarget(self.basket, self.basketStopBound)
                        if basketReached:
                            self.move.stop()
                            self.mb.sendValues()
                    else:
                        basketReached = False

                elif (self.irStatus == 1):
                    print("Throwing ball")
                    basketReached = self.throwBall(self.basket.getDistance())
                    if basketReached:
                        self.move.stop()
                        ballReached = (self.irStatus == 1)
                        ballGrabbed = ballReached
                        if ballGrabbed:
                            self.thrower.grabberCarry()
                        ballReached = False
                        basketReached = False
                        ballGrabbed = False

                else:
                    print("FIXME")
                    ballReached = False
                    basketReached = False
                    ballGrabbed = False

            if self.gameState == "STOP":
                if self.irStatus == 1:
                    self.thrower.emptyThrower()
                self.move.stop()

            #print("Run function completed in: ", effTimer.reset())
            time.sleep(1/self.mb.SENDFREQ)

        self.move.stop()

    def checkBounds(self):
        basketBounds = self.basket.verticalBounds
        blackLineBounds = self.blackLine.verticalBounds
        basketBottom = None
        lineBottom = None
        if basketBounds is not None:
            basketBottom = basketBounds[1]
        if blackLineBounds is not None:
            lineBottom = blackLineBounds[1]
        if self.basket.verticalBounds is not None:
            basketBottom = self.basket.verticalBounds[1]
        if self.blackLine.verticalBounds is not None:
            lineBottom = self.blackLine.verticalBounds[1]
        if basketBottom is not None:
            if basketBottom >= self.basketAheadBound:
                self.move.rotate(1)
        if lineBottom is not None:
            if lineBottom >= self.lineAheadBound:
                self.move.rotate(1)

    def goToTarget(self, target, verticalStopBound):
        #print(target.area)
        if target.getVerticalData() == None or target.getHorizontalData() == None:

            print("No ",  target.id, " in sight.")

            targetFound = False

            if not self.searchTimer.isStarted:
                self.searchTimer.startTimer()

            if self.searchTimer.getTimePassed() < 1000:
                targetFound = self.lookForTarget(target)
            else:
                self.searchTimer.stopTimer()
                if not targetFound:
                    for i in range(10):
                        print("Turning toward basket")
                        if (self.lookForTarget(self.basket)):
                            break
                        time.sleep(0.1)
                    if (self.basket.verticalBounds is not None and self.basket.verticalBounds[1] > self.basketStopBound):
                        self.move.driveXY(0, self.moveSpeed, 0)
            return False

        elif not self.checkVerticalAlignment(target, verticalStopBound):
            if verticalStopBound is not None:
                print("Alligning Vertically")
                #print(target.id, "'s vertical midpoint", target.getVerticalData())
                print(target.id, "'s distance: ", target.getDistance())
                self.moveTowardTarget(target)
                self.mb.sendValues()
                return False

        elif not self.checkHorizontalAlginment(target):
            print("Alligning horizontally.")
            self.turnTowardTarget(target)
            self.mb.sendValues()
            return False

        print("At position.")
        #self.move.driveXY(0, 0.3, 0)
        return True

    def initializeValues(self):
        self.frame.capture(cv2.COLOR_BGR2HSV)
        self.screenMidpoint = self.frame.width//2

    def checkHorizontalAlginment(self, target):

        horizontalMidPoint = target.getHorizontalData()
        if horizontalMidPoint is None:
            return False

        if (horizontalMidPoint < (self.screenMidpoint - self.deltaFromMidPoint)
            or horizontalMidPoint > (self.screenMidpoint + self.deltaFromMidPoint)):

            return False
        #else:
            #self.move.driveXY(0, 0.5, 0)

        print("Horizontally allgined.")
        return True

    def checkVerticalAlignment(self, target, verticalStopBound):

        stopBound = target.getVerticalData()
        if target.id == "basket" and target.getDistance() is not None:
            stopBound = 1/target.getDistance()
        else:
            print("Basket's lower coordinate not present.")
        #print(target.id, "'s vertical midpoint at the time of checking allignment: ", verticalMidPoint)
        if stopBound is None:
            self.move.stop()
            return False
        #print("Stop bound: ", stopBound)
        if stopBound < verticalStopBound:
            print("Target not reached.")
            return False
        print("Vertically alligned.")
        self.move.stop()
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
                #print("irStatus: " + str(self.irStatus))

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

        self.move.stop()
        self.mb.sendValues(wait=True)

        not_alligned = 0
        for i in range(6):
            if not self.checkHorizontalAlginment(self.basket) or not self.checkVerticalAlignment(self.basket, self.basketStopBound):
                not_alligned += 1
            time.sleep(0.033)

        if not_alligned >= 3:
            return False

        self.mb.disableFailSafe()
        self.thrower.startMotor()
        self.mb.sendValues(wait = True)
        print("Basket's distance: ", self.basket.getDistance())
        print("Basket's midpoint: ", self.basket.horizontalMidPoint)
        self.thrower.throw(distance)
        self.mb.sendValues(wait = True)

        return True
