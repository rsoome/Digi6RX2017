import math
from timer import Timer

class MovementLogic:

    def __init__(self, mb):
        self.mb = mb
        self.motorSpeed0 = 0.0
        self.motorSpeed1 = 0.0
        self.motorSpeed2 = 0.0
        self.RPS = 2.5
        self.timer = Timer.Timer()

    def drive(self, speed, angle):
        self.mb.setMotorSpeed(int(speed*(math.cos(math.radians(90 - 180 + angle)))),
                              int(speed*(math.cos(math.radians(90 - 300 + angle)))),
                              int(speed*(math.cos(math.radians(90 - 60 + angle))))) #60deg in rad
        speeds = self.mb.waitForAnswer

    def brake(self):
        pass

    def stop(self):
        self.mb.setMotorSpeed(0, 0, 0)

    def rotate(self, speed, angle):
        timeToRotate = (angle/(self.RPS * 360))/(speed/100)
        self.timer.startTimer()
        while self.timer.getTimePassed() < timeToRotate:
            self.mb.setMotorSpeed(speed, speed, speed)
            speeds = self.mb.waitForAnswer()
        self.stop()
        self.timer.stopTimer()



