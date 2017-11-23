import time

from throwingLogic import ThrowingMotor
from throwingLogic import Grabber

class Thrower:

    def __init__(self, mb):
        self.mb = mb
        self.grabber = Grabber.Grabber()
        self.throwingMotor = ThrowingMotor.ThrowingMotor()

    def calculateThrowingSpeed(self, distance):

        return 1.2597*distance + 1194

    def throw(self, distance):
        self.mb.disableFailSafe()
        self.throwingMotor.setSpeed(self.throwingMotor.MID_SPEED)
        self.mb.sendValues()
        time.sleep(0.5)
        self.mb.setThrowerSpeed(self.calculateThrowingSpeed(distance))
        self.mb.sendValues()
        time.sleep(0.8)
        self.grabberThrow()
        self.mb.sendValues()
        time.sleep(0.8)
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