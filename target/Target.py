import numpy as np
import math

# The object class, in which you can hold the coordinates of an instance. For example - a ball or a gate
from timer import Timer


class Target:

    def __init__(self, hBounds, vBounds, targetID, lowerRange, upperRange, scanOrder, minSize):
        self.setBounds(hBounds, vBounds, None)
        self.setThresholds(lowerRange, upperRange)
        print(lowerRange)
        print(upperRange)
        self.id = targetID
        self.mask = None
        self.contours = None
        self.scanOrder = scanOrder
        self.timer = Timer.Timer()
        self.minSize = minSize
        self.e = 2.7183

    def getBounds(self):
        return self.horizontalBounds, self.verticalBounds

    # Writes new values into the variables containing threshholds of a given object.
    def updateThresholds(self, values):
        # Check all the received values against current values and update if necessary
        for i in range(3):
            if values[i] < self.hsvLowerRange[i]:
                self.hsvLowerRange[i] = values[i]  # Kui väärtus on väiksem ,uuenda alumist piiri
            if values[i] > self.hsvUpperRange[i]:
                self.hsvUpperRange[i] = values[i]  # Kui väärtus on suurem, uuenda ülemist piiri
        return (self.hsvLowerRange, self.hsvUpperRange)

    def setThresholds(self, lower, upper):
        self.hsvLowerRange = np.array(lower)
        self.hsvUpperRange = np.array(upper)

    def resetThreshHolds(self):
        self.hsvLowerRange = np.array(
            [255, 255, 255])
        self.hsvUpperRange = np.array(
            [0, 0, 0])

    def resetBounds(self):
        self.setBounds(None, None, None)

    def setBounds(self, hBounds, vBounds, area):
        self.horizontalBounds = hBounds
        self.verticalBounds = vBounds
        self.area = area

        if hBounds != None:
            if self.horizontalMidPoint != None:
                self.horizontalMidPoint = (self.horizontalMidPoint + (hBounds[0] + (hBounds[1] - hBounds[0]) // 2))//2
            else:
                self.horizontalMidPoint = hBounds[0] + (hBounds[1] - hBounds[0]) // 2
        else:
            self.horizontalMidPoint = None

        if vBounds != None:
            #print(self.verticalMidPoint)
            self.verticalMidPoint = vBounds[0] + (vBounds[1] - vBounds[0]) // 2
        else:
            self.verticalMidPoint = None

    def getDistance(self):
        if self.verticalBounds is None:
            return None

        #return self.verticalBounds[1]
        if self.verticalBounds[1] >= 284:
            return -0.1701*self.verticalBounds[1] + 77.502

        return 101513*pow(self.verticalBounds[1], -1.414)