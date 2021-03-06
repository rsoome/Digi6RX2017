class Grabber:

    def __init__(self, mb):
        self.mb = mb
        self.MAX_POSITION = 2350
        self.MIN_POSITION = 550
        self.CARRY_POSITION = 1900
        self.THROW_POSITION = 800
        self.OPEN_POSITION = 2150

    def setPosition(self, position):
        self.mb.setGrabberPosition(min(max(position, self.MIN_POSITION), self.MAX_POSITION))
        self.mb.sendValues()