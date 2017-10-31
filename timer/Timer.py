from datetime import datetime

class Timer:

    def __init__(self):
        self.start = None

    def startTimer(self):
        self.start = self.getTimeInMillis()

    def stopTimer(self):
        time = self.getTimePassed()
        self.start = None
        return time

    def getTimePassed(self):
        time = -1
        stop = self.getTimeInMillis()
        if self.start != None:
            time = stop - self.start
        return time

    def getTimeInMillis(self):
        return int(float(str(datetime.now()).split()[1].split(":")[2]) * 1000)