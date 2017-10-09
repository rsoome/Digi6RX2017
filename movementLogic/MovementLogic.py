import math
import re

class MovementLogic:

    def __init__(self, mb):
        self.mb = mb

    def drive(self, speed):
        self.mb.setMotorSpeed(speed*(math.cos(2.09439510)), speed*(math.cos(4.1887902)), speed*(math.cos(0))) #60deg in rad

    def brake(self):
        speeds = self.mb.getMotorSpeed()
        speeds = re.split(":|sd", speeds)
        print(speeds)
        #self.mb.setMotorSpeed(int(speeds[0]), int(speeds[1]), int(speeds[2]))

    def rotate(self, speed):
        self.mb.setMotorSpeed(speed, speed, speed)
