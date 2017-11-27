from datetime import datetime

class Timer:

    def __init__(self):
        self.start = None
        self.isStartd = False

    def startTimer(self):
        self.isStartd = True
        self.start = self.getTimeInMillis()

    def stopTimer(self):
        self.isStartd = False
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

    def reset(self):
        time = self.stopTimer()
        self.startTimer()
        return time