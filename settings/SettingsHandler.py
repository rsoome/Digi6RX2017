class SettingsHandler:

    def __init__(self, fileLocation):
        self.fileLoc = fileLocation
        self.values = dict()
        self.initializeSettings()

    def readFromFileToDict(self):
        with open(self.fileLoc, "r") as f:
            d = dict()
            line = f.readline()

            while line != '':
                d[line.split(" = ")[0]] = line.split(" = ")[1].strip()
                line = f.readline()

            return d

    def getValue(self, key):
        if key in self.values:
            return self.values[key]
        return ""

    def setValue(self, key, value):
        self.values[key] = str(value)

    def writeFromDictToFile(self):
        newValues = ""
        for key in self.values:
            newValues += str(key) + " = " + str(self.values[key]) + "\n"

        with open(self.fileLoc, "w") as f:
            f.write(newValues)

    def initializeSettings(self):

        try:
            self.values = self.readFromFileToDict()
        except FileNotFoundError:
            with open(self.fileLoc, "w"):
                pass

        if not "driveSpeed" in self.values:
            self.values["driveSpeed"] = "10"
        if not "turnSpeed" in self.values:
            self.values["turnSpeed"] = "10"
        if not "camID" in self.values:
            self.values["camID"] = "0"
        if not "multiThreading" in self.values:
            self.values["multiThreading"] = "True"
        if not "ballHSVLower" in self.values:
            self.values["ballHSVLower"] = "255 255 255"
        if not "ballHSVHigher" in self.values:
            self.values["ballHSVUpper"] = "0 0 0"
        if not "basketHSVLower" in self.values:
            self.values["basketHSVLower"] = "255 255 255"
        if not "basketHSVHigher" in self.values:
            self.values["basketHSVUpper"] = "0 0 0"
        if not "mbLocation = " in self.values:
            self.values["mbLocation"] = "/dev/ttyACM0"
        if not "ballScanOrder" in self.values:
            self.values["ballScanOrder"] = "1 0 2 4 3 5 7 6 8"
        if not "basketScanOrder" in self.values:
            self.values["basketScanOrder"] = "7 6 8 4 3 5 1 0 2"
        if not "objectMinSize" in self.values:
            self.values["objectMinSize"] = "1000"
        if not "minImgArea" in self.values:
            self.values["minImgArea"] = "0"