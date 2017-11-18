import numpy as np

# The object class, in which you can hold the coordinates of an instance. For example - a ball or a gate
class Target:

    def __init__(self, hBounds, vBounds, targetID, lowerRange, upperRange, scanOrder):
        self.setBounds(hBounds, vBounds)
        self.setThresholds(lowerRange, upperRange)
        self.id = targetID
        self.mask = None
        self.contours = None
        self.scanOrder = scanOrder

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
        self.setBounds(None, None)

    def setBounds(self, hBounds, vBounds):
        self.horizontalBounds = hBounds
        self.verticalBounds = vBounds


        if hBounds != None:
            self.horizontalMidPoint = hBounds[0] + (hBounds[1] - hBounds[0]) // 2
        else:
            self.horizontalMidPoint = None

        if vBounds != None:
            #print(self.verticalMidPoint)
            self.verticalMidPoint = vBounds[0] + (vBounds[1] - vBounds[0]) // 2
        else:
            self.verticalMidPoint = None
