import math

class MovementLogic:

    def __init__(self, mb):
        self.mb = mb
        self.motorSpeed0 = 0.0
        self.motorSpeed1 = 0.0
        self.motorSpeed2 = 0.0
        self.minTurnSpeed = 0.2
        self.wheelDistance = 0.13
        self.currentSpeed = 0.1
        self.currentTurnSpeed = 0.2

        self.wheelSpeedToMainboardUnits = 18.75 * 64 / (2 * math.pi * 0.035 * 60)

    def drive(self, speed, angle, omega):
        if speed != 0:
            self.currentSpeed = speed
        if omega != 0:
            self.currentTurnSpeed = omega
        print("Omega: ", omega)
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
        speed = math.sqrt(pow(speedX, 2) + pow(speedY, 2))
        self.drive(speed, angle, omega)

    def calculateSpeed(self, maxSpeed, verticalMidPoint):
        coif = 1.6211 * pow(math.e, -0.005*verticalMidPoint)

        #print("verticalMidPoint: ", verticalMidPoint)
        #print("coif: ", coif)

        if coif > 0.7:
            return maxSpeed

        if coif < 0.1 :
            return 0.1 * maxSpeed

        return coif * maxSpeed

    def calculateOmega(self, maxSpeed, horizontalMidPoint):
        coif = 0.0985*pow(math.e, 0.0113 * horizontalMidPoint)

        if coif > 0.5:
            return maxSpeed
        if horizontalMidPoint < 320:
            return -coif*maxSpeed
        return coif*maxSpeed

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
        if speed < 0:
            self.driveXY(0,0,speed - self.minTurnSpeed)
        if speed > 0:
            self.driveXY(0, 0, speed + self.minTurnSpeed)

    def updateSpeeds(self, speeds):
        if speeds[0] == "motors" and len(speeds == 4):
            self.motorSpeed0 = float(speeds[1])
            self.motorSpeed1 = float(speeds[2])
            self.motorSpeed2 = float(speeds[3])

