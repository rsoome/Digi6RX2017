import math
import re

class MovementLogic:

    def __init__(self, mb):
        self.mb = mb
        self.motorSpeed0 = 0.0
        self.motorSpeed1 = 0.0
        self.motorSpeed2 = 0.0

    def drive(self, speed, angle):
        self.mb.setMotorSpeed(int(speed*(math.cos(math.radians(90 - 180 + angle)))),
                              int(speed*(math.cos(math.radians(90 - 300 + angle)))),
                              int(speed*(math.cos(math.radians(90 - 60 + angle))))) #60deg in rad

    def brake(self):
        pass

    def stop(self):
        self.mb.setMotorSpeed(0, 0, 0)

    def rotate(self, speed):
        self.mb.setMotorSpeed(speed, speed, speed)
