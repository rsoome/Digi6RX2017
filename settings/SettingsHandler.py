import json
import numpy as np

class SettingsHandler:

    def __init__(self, fileLocation):
        self.fileLoc = fileLocation
        self.values = dict()
        self.initializeSettings()

    def readFromFileToDict(self):
        with open(self.fileLoc, "r") as f:
            return json.loads(f.read())

    def getValue(self, key):
        if key in self.values:
            return self.values[key]
        return ""

    def setValue(self, key, value):
        self.values[key] = value

    def writeFromDictToFile(self):
        with open(self.fileLoc, "w") as f:
            return f.write(json.dumps(self.values, indent=1, sort_keys=True))

    def initializeSettings(self):

        try:
            self.values = self.readFromFileToDict()
        except FileNotFoundError:
            with open(self.fileLoc, "w"):
                pass

        if not "driveSpeed" in self.values:
            self.values["driveSpeed"] = 10
        if not "turnSpeed" in self.values:
            self.values["turnSpeed"] = 10
        if not "camID" in self.values:
            self.values["camID"] = 0
        if not "multiThreading" in self.values:
            self.values["multiThreading"] = True
        if not "ballHSVLower" in self.values:
            self.values["ballHSVLower"] = [255, 255, 255]
        if not "ballHSVHigher" in self.values:
            self.values["ballHSVUpper"] = [0, 0, 0]
        if not "magnetaBasketHSVLower" in self.values:
            self.values["magnetaBasketHSVLower"] = [255, 255, 255]
        if not "magnetaBasketHSVHigher" in self.values:
            self.values["magnetaBasketHSVUpper"] = [0, 0, 0]
        if not "blueBasketHSVLower" in self.values:
            self.values["blueBasketHSVLower"] = [255, 255, 255]
        if not "blueBasketHSVHigher" in self.values:
            self.values["blueBasketHSVUpper"] = [0, 0, 0]
        if not "mbLocation = " in self.values:
            self.values["mbLocation"] = "/dev/ttyACM0"
        if not "ballScanOrder" in self.values:
            self.values["ballScanOrder"] = [1, 0, 2, 4, 3, 5, 7, 6, 8]
        if not "basketScanOrder" in self.values:
            self.values["basketScanOrder"] = [7, 6, 8, 4, 3, 5, 1, 0, 2]
        if not "objectMinSize" in self.values:
            self.values["objectMinSize"] = 1000
        if not "minImgArea" in self.values:
            self.values["minImgArea"] = 0
        if not "ID" in self.values:
            self.values["ID"] = None
        if not "fieldID" in self.values:
            self.values["fieldID"] = None
        if not "defaultGameState" in self.values:
            self.values["defaultGameState"] = "STOP"
        if not "opponentBasket" in self.values:
            self.values["opponentBasket"] = None