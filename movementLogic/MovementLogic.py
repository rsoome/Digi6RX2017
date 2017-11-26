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
        self.currentSpeed = 0
        self.currentTurnSpeed = 0

        self.wheelSpeedToMainboardUnits = 18.75 * 64 / (2 * math.pi * 0.035 * 60)

    def drive(self, speed, angle, omega):
        self.currentSpeed = speed
        self.currentTurnSpeed = omega
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
        return (-8 * pow(10, -6) * pow(coif, 2) + 0.0019 * coif + 0.08851) * maxSpeed

    def calculateOmega(self, maxSpeed, coif):
        if coif == 0:
            return 0
        returnSpeed = coif/abs(coif) * ((0.3162*math.log(coif) - 1.0766) * maxSpeed)
        if (coif > -0.1 and returnSpeed < 0) or (coif < 0.1 and returnSpeed > 0):
            return 0
        return returnSpeed

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

