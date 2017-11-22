import cv2
import time

import math

from timer import Timer
# Contins the game logic
# TODO: Implement
class GameLogic:

    def __init__(self, move, deltaFromMidPoint, moveSpeed, turnSpeed, frame, socketData, ref, fieldID, robotID, mb,
                 ball, basket, defaultGameState):
        self.frameWidth = None
        self.move = move
        self.deltaFromMidPoint = deltaFromMidPoint
        self.moveSpeed = moveSpeed
        self.turnSpeed = turnSpeed
        self.frame = frame
        self.initializeValues()
        self.socketData = socketData
        self.ballStopBound = frame.height + 80
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
        self.timer = Timer.Timer()
        self.IRCONFIRMATIONSNEEDED = 100

    def turnTowardTarget(self, target):
        if target.horizontalMidPoint == None:
            return False
        turnCoificent = (target.horizontalMidPoint - self.screenMidpoint)/float(self.screenMidpoint)
        print("Turncoificent: " + str(turnCoificent))
        if target.horizontalMidPoint is not None:
            if not self.socketData.gameStarted:
                return False
            turningSpeed = self.move.calculateSpeed(self.turnSpeed, turnCoificent)
            print("Turning with speed: " + str(turningSpeed))
            self.move.driveXY(0,0,turningSpeed)
            return True

    def moveTowardTarget(self, target):
        if target.horizontalMidPoint is not None:

            if target.verticalMidPoint is None:
                return

            if not self.socketData.gameStarted:
                return

            #print("Verticalmidpoint: " + str(target.verticalMidPoint))
            #print("Jagamine: " + str(1 - float(target.verticalMidPoint)/self.frame.height))
            #print("moveSpeed" + str(self.moveSpeed))
            #print("CalculateSpeed: " + str(self.move.calculateSpeed(self.moveSpeed, 1 - float(target.verticalMidPoint)/self.frame.height)))
            self.move.driveXY(0,

                              self.move.calculateSpeed(self.moveSpeed, 1 - float(target.verticalMidPoint)/self.frame.height),
                              #  0)
                              self.move.calculateSpeed(self.turnSpeed,
                                                       (target.horizontalMidPoint - self.screenMidpoint) / float(self.screenMidpoint))
                              )

    def lookForTarget(self, target):
        #if not self.socketData.gameStarted:
        if False:
            print("Game ended by client.")
            return False

        #print(target.horizontalMidPoint)
        self.move.driveXY(0,0,self.turnSpeed)
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
        irConfirmations = 0

        while self.socketData.gameStarted:
            self.timer.startTimer()
            self.readMb()

            if self.mb.sendingTime():
                self.mb.sendValues()

            if self.gameState == "START":

                if self.irStatus == 1:
                    irConfirmations += 1
                    if irConfirmations >= self.IRCONFIRMATIONSNEEDED:
                        ballReached = True
                        ballGrabbed = True
                else:
                    irConfirmations -= 1
                    if irConfirmations <= -self.IRCONFIRMATIONSNEEDED:
                        ballReached = False
                        ballGrabbed = False
                        irConfirmations = 0

                if ballGrabbed:
                    self.mb.setGrabberPosition(self.mb.GRABBER_CARRY_POSITION)

                if not ballReached:
                    print("Going to ball")
                    self.mb.setGrabberPosition(self.mb.GRABBER_OPEN_POSITION)
                    ballReached = self.goToTarget(self.ball, self.ballStopBound, self.moveSpeed)

                elif ballReached and not ballGrabbed:
                    print("Reaching ball")
                    self.move.driveXY(0, self.moveSpeed//50, 0)
                    time.sleep(0.1)
                    ballGrabbed = self.irStatus == 1
                    if ballGrabbed:
                        self.mb.setGrabberPosition(self.mb.GRABBER_CARRY_POSITION)
                        self.mb.setThrowerSpeed(self.mb.THROWER_MINSPEED)
                    else:
                        self.mb.setGrabberPosition(self.mb.GRABBER_OPEN_POSITION)
                        self.mb.setThrowerSpeed(self.mb.THROWER_STOP)
                    self.mb.sendValues()

                elif not basketReached:
                    print("Reaching basket")
                    basketReached = self.goToTarget(self.basket, self.basketStopBound, self.moveSpeed)

                elif (self.irStatus == 1):
                    self.move.stop()
                    throwTimer = Timer.Timer()
                    print("Throwing ball")
                    self.move.stop()
                    basketReached = self.throwBall()
                    if basketReached:
                        ballReached = (self.irStatus == 1)
                        ballGrabbed = ballReached
                        if ballGrabbed:
                            self.mb.setGrabberPosition(self.mb.GRABBER_CARRY_POSITION)
                        throwTimer.startTimer()
                        while throwTimer.getTimePassed() < 1000:
                            self.mb.readInfrared()
                            time.sleep(0.1)
                        ballReached = False
                        basketReached = False
                        ballGrabbed = False
                        throwTimer.stopTimer()

                else:
                    print("FIXME")

            if self.gameState == "STOP":
                self.emptyThrower()
                self.move.stop()

            self.addFrame(self.timer.stopTimer())
            self.updateFPS()

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
                for i in range(2000):
                    #print(i)
                    self.move.driveXY(0, self.moveSpeed//4, 0)
                    self.move.stop()
                return False

        elif not self.checkVerticalAlignment(target, verticalStopBound):
            print("Alligning Vertically")
            self.moveTowardTarget(target)
            return False

        elif not self.checkHorizontalAlginment(target):
            print("Alligning horizontally.")
            self.move.stop()
            self.turnTowardTarget(target)
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

        #print(stopArea)
        #print(target.area)
        #print(target.area > stopArea)
        if target.area is None:
            return False

        if target.verticalMidPoint >= verticalStopBound:
            return False
        print("Vertically alligned.")
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

    def throwBall(self):
        if not self.checkHorizontalAlginment(self.basket) or not self.checkVerticalAlignment(self.basket, self.basketStopBound):
            return False
        self.mb.setThrowerSpeed(self.mb.THROWER_MIDSPEED)
        self.mb.disableFailSafe()
        self.mb.sendValues()
        time.sleep(0.5)
        self.mb.setThrowerSpeed(self.mb.THROWER_MAXSPEED)
        self.mb.sendValues()
        time.sleep(1.3)
        self.mb.setGrabberPosition(self.mb.GRABBER_THROW_POSITION)
        self.mb.sendValues()
        time.sleep(1)
        self.mb.enableFailSafe()
        self.mb.setThrowerSpeed(self.mb.THROWER_STOP)
        self.mb.setGrabberPosition(self.mb.GRABBER_OPEN_POSITION)
        self.mb.sendValues()
        print("throwing irStatus " + str(self.irStatus))
        return self.irStatus == 0

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

    def emptyThrower(self):
        self.mb.disableFailSafe()
        self.mb.setThrowerSpeed(self.mb.THROWER_MINSPEED)
        self.mb.sendValues()
        time.sleep(0.5)
        self.mb.setThrowerSpeed(self.mb.THROWER_MIDSPEED)
        self.mb.sendValues()
        time.sleep(0.5)
        #self.mb.setThrowerSpeed(self.mb.THROWER_MAXSPEED)
        #self.mb.sendValues()
        #time.sleep(0.5)
        self.mb.setGrabberPosition(self.mb.GRABBER_THROW_POSITION)
        self.mb.sendValues()
        time.sleep(0.5)
        self.mb.enableFailSafe()
        self.mb.setGrabberPosition(self.mb.GRABBER_OPEN_POSITION)
        self.mb.setThrowerSpeed(self.mb.THROWER_STOP)
        self.mb.sendValues()
