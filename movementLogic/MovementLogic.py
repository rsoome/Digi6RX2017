import math

class MovementLogic:

    def __init__(self, mb):
        self.mb = mb

    def drive(self, speed):
        self.mb.setMotorSpeed(speed*(math.cos(1.04719755)), speed*(math.cos(-1.04719755 )), speed*(math.cos(0))) #60deg in rad

    def brake(self):
        speeds = self.mb.getMotorSpeed()
        speeds = speeds.split(":")
        self.mb.setMotorSpeed(int(speeds[0]), int(speeds[1]), int(speeds[2]))

    def rotate(self, speed):
        self.mb.setMotorSpeed(speed, speed, speed)