import math
import re

class MovementLogic:

    def __init__(self, mb):
        self.mb = mb

    def drive(self, speed, angle):
        self.mb.setMotorSpeed(speed*(math.cos(math.radians(90 - 120 + angle))),
                              speed*(math.cos(math.radians(90 - 240 + angle))),
                              speed*(math.cos(math.radians(90 + angle)))) #60deg in rad
        print(math.cos(math.radians(90 + angle)))

    def brake(self):
        speeds = self.mb.getMotorSpeed()
        speeds = re.split(":|sd", speeds)
        print(speeds)
        #self.mb.setMotorSpeed(int(speeds[0]), int(speeds[1]), int(speeds[2]))

    def rotate(self, speed):
        self.mb.setMotorSpeed(speed, speed, speed)
