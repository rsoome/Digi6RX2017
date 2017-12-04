import time

import math

from throwingLogic import ThrowingMotor
from throwingLogic import Grabber

class Thrower:

    def __init__(self, mb):
        self.mb = mb
        self.grabber = Grabber.Grabber(mb)
        self.throwingMotor = ThrowingMotor.ThrowingMotor(mb)

    def calculateThrowingSpeed(self, distance):
        if distance is None:
            return self.throwingMotor.MIN_SPEED
        if distance < 40:
            return 1450
        if distance < 85:
            return 0.0461 * pow(distance, 2) - 4.7981 * distance + 1495 #1463.8
        return 180.81 * math.log(distance) + 615#180.81, 583.45

    def throw(self, distance):
        print("Setting throw speed to :" + str(self.calculateThrowingSpeed(distance)))
        print("Throwing at: ", distance)
        self.setMotorSpeed(self.calculateThrowingSpeed(distance))
        self.mb.sendValues(wait = True)
        time.sleep(1)
        print("Throwing.")
        self.grabberThrow()
        self.mb.sendValues(wait = True)
        time.sleep(0.8)
        print("Enabling failsafe and stopping motor.")
        self.mb.enableFailSafe()
        self.stopMotor()
        self.grabberOpen()
        self.mb.sendValues(wait = True)

    def startMotor(self):
        self.throwingMotor.setSpeed(self.throwingMotor.MIN_SPEED)

    def stopMotor(self):
        self.throwingMotor.stop()

    def setMotorSpeed(self, speed):
        self.throwingMotor.setSpeed(speed)

    def grabberOpen(self):
        self.grabber.setPosition(self.grabber.OPEN_POSITION)

    def grabberCarry(self):
        self.grabber.setPosition(self.grabber.CARRY_POSITION)

    def grabberThrow(self):
        self.grabber.setPosition(self.grabber.THROW_POSITION)

    def emptyThrower(self):
        self.throw(0)
