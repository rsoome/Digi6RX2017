from datetime import datetime

class Timer:

    def __init__(self):
        self.start = None

    def startTimer(self):
        self.start = self.getTimeInMicros()

    def stopTimer(self):
        time = -1
        stop = self.getTimeInMicros()
        if self.start != None:
            time = self.start - stop
        self.start = None
        return time

    def getTimeInMicros(self):
        return float(str(datetime.now()).split()[1].split(":")[2]) *1000000