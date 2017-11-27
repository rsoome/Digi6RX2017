import time

class Timer:

    def __init__(self):
        self.start = None
        self.isStarted = False

    def startTimer(self):
        self.isStarted = True
        self.start = self.getTimeInMillis()

    def stopTimer(self):
        self.isStarted = False
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
        return int(round(time.time()) * 1000)

    def reset(self):
        time = self.stopTimer()
        self.startTimer()
        return time