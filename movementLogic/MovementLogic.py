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
        self.minDriveSpeed = 0.1
        self.minTurnSpeed = 0.3
        self.wheelDistance = 0.13

        self.wheelSpeedToMainboardUnits = 18.75 * 64 / (2 * math.pi * 0.035 * 60)

    def drive(self, speed, angle, omega):
        '''print("Omega: " + str(omega))
        print("Motor 0: " + str(self.wheelSpeedToMainboardUnits* (speed*(math.cos(math.radians(90 - 180 + angle)))
                                  + omega*self.wheelDistance)))
        print("Motor 1: " + str(self.wheelSpeedToMainboardUnits * (speed * (math.cos(math.radians(90 - 300 + angle)))
                                + omega * self.wheelDistance)))
        print("Motor 2: " + str(self.wheelSpeedToMainboardUnits * (speed * (math.cos(math.radians(90 - 60 + angle)))
                                + omega * self.wheelDistance)))'''

        self.mb.setMotorSpeed(int(self.wheelSpeedToMainboardUnits*(speed*(math.cos(math.radians(90 - 180 + angle)))
                                  + omega*self.wheelDistance)),
                              int(self.wheelSpeedToMainboardUnits*(speed*(math.cos(math.radians(90 - 300 + angle)))
                                  + omega*self.wheelDistance)),
                              int(self.wheelSpeedToMainboardUnits*(speed*(math.cos(math.radians(90 - 60 + angle))))
                                + omega*self.wheelDistance))

    def driveXY(self, speedX, speedY, omega):
        angle = math.atan2(speedX, speedY)
        speed = math.sqrt(pow(speedX, 2) + pow(speedY, 2)) + self.minDriveSpeed
        self.drive(speed, angle, omega)

    def calculateSpeed(self, maxSpeed, coif):
        return (-8*pow(10, -6)*pow(coif, 2) + 0.0073*coif - 0.6257)* maxSpeed

    def calculateOmega(self, maxSpeed, coif):
        return max(coif/abs(coif) * ((0.4446*math.log(abs(coif)) - 1.9015) * maxSpeed), 0)

    def brake(self):
        print(self.motorSpeed0)
        print(self.motorSpeed1)
        print(self.motorSpeed2)
        while self.motorSpeed0 > 0 or self.motorSpeed1 > 0 or self.motorSpeed2 > 0:
            self.updateSpeeds(speeds)
            speeds = self.mb.setMotorSpeed(-self.motorSpeed0, -self.motorSpeed1, -self.motorSpeed2)


    def stop(self):
        self.mb.setMotorSpeed(0, 0, 0)
        self.mb.sendValues()

    def rotate(self, speed):
        self.driveXY(0,0,speed + self.minTurnSpeed)

    def updateSpeeds(self, speeds):
        if speeds[0] == "motors" and len(speeds == 4):
            self.motorSpeed0 = float(speeds[1])
            self.motorSpeed1 = float(speeds[2])
            self.motorSpeed2 = float(speeds[3])

