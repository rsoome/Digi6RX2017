import math

import time

from timer import Timer

class MovementLogic:

    def __init__(self, mb):
        self.mb = mb
        self.motorSpeed0 = 0.0
        self.motorSpeed1 = 0.0
        self.motorSpeed2 = 0.0
        self.RPS = 1.33
        self.timer = Timer.Timer()

    def drive(self, speed, angle):
        self.mb.setMotorSpeed(int(speed*(math.cos(math.radians(90 - 180 + angle)))),
                              int(speed*(math.cos(math.radians(90 - 300 + angle)))),
                              int(speed*(math.cos(math.radians(90 - 60 + angle))))) #60deg in rad
        return self.mb.waitForAnswer
        #time.sleep(0.001)

    def brake(self):
        print(self.motorSpeed0)
        print(self.motorSpeed1)
        print(self.motorSpeed2)
        while self.motorSpeed0 > 0 or self.motorSpeed1 > 0 or self.motorSpeed2 > 0:
            self.updateSpeeds(speeds)
            speeds = self.mb.setMotorSpeed(-self.motorSpeed0, -self.motorSpeed1, -self.motorSpeed2)


    def stop(self):
        self.mb.setMotorSpeed(0, 0, 0)

    def rotate(self, speed, angle):
        timeToRotate = (angle / ((self.RPS*(speed/100)) * 360)) * 1000
        print(timeToRotate)
        #self.mb.disableFailSafe()
        self.mb.setMotorSpeed(speed, speed, speed)
        self.timer.startTimer()
        timePassed = self.timer.getTimePassed()
        while timePassed < timeToRotate:
            speeds = self.mb.setMotorSpeed(speed, speed, speed)
            self.updateSpeeds(speeds)
            timePassed = self.timer.getTimePassed()
            print(timePassed)
        #self.mb.enableFailSafe()
        self.stop()
        print("Rotation completed")
        self.timer.stopTimer()

    def updateSpeeds(self, speeds):
        if speeds[0] == "motors" and len(speeds == 4):
            self.motorSpeed0 = float(speeds[1])
            self.motorSpeed1 = float(speeds[2])
            self.motorSpeed2 = float(speeds[3])

