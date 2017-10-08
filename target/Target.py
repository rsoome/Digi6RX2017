import numpy as np

# The object class, in which you can hold the coordinates of an instance. For example - a ball or a gate
class Target:

    def __init__(self, hBounds, vBounds, targetID, lowerRange, upperRange):
        self.horizontalBounds = hBounds
        self.verticalBounds = vBounds
        # HSV värviruumi alumine piir, hilisemaks filtreerimiseks TODO: Kirjuta faili
        self.hsvLowerRange = lowerRange
        # HSV värviruumi ülemine piir, hilisemaks filtreerimiseks TODO: Kirjuta faili
        self.hsvUpperRange = upperRange
        self.id = targetID

    def getBounds(self):
        return self.horizontalBounds, self.verticalBounds

    # Writes new values into the variables containing threshholds of a given object.
    def updateThresholds(self, values):
        print("Updating " + str(self.id) + "'s thresholds.")
        # Check all the received values against current values and update if necessary
        for i in range(3):
            if values[i] < self.hsvLowerRange[i]:
                self.hsvLowerRange[i] = values[i]  # Kui väärtus on väiksem ,uuenda alumist piiri
            if values[i] > self.hsvUpperRange[i]:
                self.hsvUpperRange[i] = values[i]  # Kui väärtus on suurem, uuenda ülemist piiri

    def resetThreshHolds(self):
        self.hsvLowerRange = np.array(
            [255, 255, 255])
        self.hsvUpperRange = np.array(
            [0, 0, 0])

    def resetBounds(self):
        self.horizontalBounds = None
        self.verticalBounds = None

    def setBounds(self, hBounds, vBounds):
        self.horizontalBounds = hBounds
        self.verticalBounds = vBounds