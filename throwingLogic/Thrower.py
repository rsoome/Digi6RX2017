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

        return -0.003*pow(distance, 2) + 2.0342 * distance + 1300

    def throw(self, distance):
        print("Disabling failsafe.")
        self.mb.disableFailSafe()
        print("Warming thrower.")
        self.startMotor()
        self.mb.sendValues()
        time.sleep(0.8)
        print("Setting throw speed to :" + str(self.calculateThrowingSpeed(distance)))
        self.setMotorSpeed(self.calculateThrowingSpeed(distance))
        self.mb.sendValues()
        time.sleep(0.8)
        print("Throwing.")
        self.grabberThrow()
        self.mb.sendValues()
        time.sleep(0.8)
        print("Enabling failsafe and stopping motor.")
        self.mb.enableFailSafe()
        self.stopMotor()
        self.grabberOpen()
        self.mb.sendValues()

    def startMotor(self):
        self.throwingMotor.setSpeed(self.throwingMotor.MIN_SPEED)

    def stopMotor(self):
        self.throwingMotor.setSpeed(self.throwingMotor.STOP_SPEED)

    def setMotorSpeed(self, speed):
        self.throwingMotor.setSpeed(speed)

    def grabberOpen(self):
        self.grabber.setPosition(self.grabber.OPEN_POSITION)
        time.sleep(0.5)

    def grabberCarry(self):
        self.grabber.setPosition(self.grabber.CARRY_POSITION)
        time.sleep(0.5)

    def grabberThrow(self):
        self.grabber.setPosition(self.grabber.THROW_POSITION)
        time.sleep(0.5)

    def emptyThrower(self):
        self.throw(0)