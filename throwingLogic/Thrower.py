import time

from throwingLogic import ThrowingMotor
from throwingLogic import Grabber

class Thrower:

    def __init__(self, mb):
        self.mb = mb
        self.grabber = Grabber.Grabber(mb)
        self.throwingMotor = ThrowingMotor.ThrowingMotor(mb)

    def calculateThrowingSpeed(self, distance):

        return 0.0004*distance + 0.4155 * distance + 150

    def throw(self, distance):
        print("Disabling failsafe.")
        self.mb.disableFailSafe()
        print("Warming thrower.")
        self.throwingMotor.setSpeed(self.throwingMotor.MID_SPEED)
        self.mb.sendValues()
        time.sleep(1)
        print("Setting throw speed.")
        self.mb.setThrowerSpeed(self.calculateThrowingSpeed(distance))
        self.mb.sendValues()
        time.sleep(1)
        print("Throwing.")
        self.grabberThrow()
        self.mb.sendValues()
        time.sleep(0.8)
        print("Enabling failsafe and stopping motor.")
        self.mb.enableFailSafe()
        self.throwingMotor.setSpeed(self.throwingMotor.STOP_SPEED)
        self.grabberOpen()
        self.mb.sendValues()

    def startMotor(self):
        self.throwingMotor.setSpeed(self.throwingMotor.MIN_SPEED)

    def stopMotor(self):
        self.throwingMotor.setSpeed(self.throwingMotor.STOP_SPEED)

    def grabberOpen(self):
        self.grabber.setPosition(self.grabber.OPEN_POSITION)

    def grabberCarry(self):
        self.grabber.setPosition(self.grabber.CARRY_POSITION)

    def grabberThrow(self):
        self.grabber.setPosition(self.grabber.THROW_POSITION)

    def emptyThrower(self):
        self.throw(0)