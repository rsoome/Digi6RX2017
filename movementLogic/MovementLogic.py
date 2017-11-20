import math

import time

from timer import Timer

class MovementLogic:

    def __init__(self, mb):
        self.mb = mb
        self.motorSpeed0 = 0.0
        self.motorSpeed1 = 0.0
        self.motorSpeed2 = 0.0
        self.timer = Timer.Timer()
        self.minDriveSpeed = 10

    def drive(self, speed, angle, omega):
        self.mb.setMotorSpeed(int(speed*(math.cos(math.radians(90 - 180 + angle))) + omega),
                              int(speed*(math.cos(math.radians(90 - 300 + angle))) + omega),
                              int(speed*(math.cos(math.radians(90 - 60 + angle)))) + omega)
        return self.mb.waitForAnswer

    def driveXY(self, speed, coifX, coifY, turnSpeed):
        speedX = coifX * speed + self.minDriveSpeed
        speedY = coifY * speed + self.minDriveSpeed
        omega = speedX * turnSpeed
        angle = math.atan2(speedX, speedY)
        speed = math.sqrt(pow(speedX, 2) + pow(speedY, 2))
        self.drive(speed, angle, omega)

    def brake(self):
        print(self.motorSpeed0)
        print(self.motorSpeed1)
        print(self.motorSpeed2)
        while self.motorSpeed0 > 0 or self.motorSpeed1 > 0 or self.motorSpeed2 > 0:
            self.updateSpeeds(speeds)
            speeds = self.mb.setMotorSpeed(-self.motorSpeed0, -self.motorSpeed1, -self.motorSpeed2)


    def stop(self):
        self.mb.setMotorSpeed(0, 0, 0)

    def rotate(self, speed):
        self.mb.setMotorSpeed(speed, speed, speed)

    def updateSpeeds(self, speeds):
        if speeds[0] == "motors" and len(speeds == 4):
            self.motorSpeed0 = float(speeds[1])
            self.motorSpeed1 = float(speeds[2])
            self.motorSpeed2 = float(speeds[3])

