import math
import re

class MovementLogic:

    def __init__(self, mb):
        self.mb = mb

    def drive(self, speed, angle):
        self.mb.setMotorSpeed(speed*(math.cos(2.09439510 + math.radians(angle))),
                              speed*(math.cos(4.1887902 + math.radians(angle))),
                              speed*(math.cos(0 + math.radians(angle)))) #60deg in rad

    def brake(self):
        speeds = self.mb.getMotorSpeed()
        speeds = re.split(":|sd", speeds)
        print(speeds)
        #self.mb.setMotorSpeed(int(speeds[0]), int(speeds[1]), int(speeds[2]))

    def rotate(self, speed):
        self.mb.setMotorSpeed(speed, speed, speed)
