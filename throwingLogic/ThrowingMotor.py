class ThrowingMotor:

    def __init__(self, mb):
        self.mb = mb
        self.MIN_SPEED = 1400
        self.MAX_SPEED = 2150
        self.MID_SPEED = (self.MIN_SPEED + self.MAX_SPEED) // 2
        self.STOP_SPEED = 500

    def setSpeed(self, speed):
        self.mb.setThrowerSpeed(min(max(speed, self.MIN_SPEED), self.MAX_SPEED))

    def stop(self):
        self.mb.setThrowerSpeed(self.STOP_SPEED)