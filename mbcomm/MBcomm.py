import serial

class MBcomm:

    def __init__(self, target, baud):
        self.ser = serial.Serial(port=target, baudrate=baud, timeout=0.8)
        self.THROWER_MAXSPEED = 2000
        self.THROWER_MINSPEED = 1200
        self.THROWER_CONSTANT = (self.THROWER_MINSPEED + self.THROWER_MAXSPEED)
        self.THROWER_MIDSPEED = self.THROWER_CONSTANT // 2
        self.THROWER_STOP = 1000
        self.GRABBER_MAX_POSITION = 2350
        self.GRABBER_MIN_POSITION = 550
        self.GRABBER_CARRY_POSITION = self.GRABBER_MAX_POSITION / 3 + self.GRABBER_MIN_POSITION
        self.GRABBER_THROW_POSITION = self.GRABBER_MIN_POSITION
        self.GRABBER_OPEN_POSITION = self.GRABBER_MAX_POSITION - 100
        if not self.ser.isOpen():
            self.ser.open()

    def __sendBytes(self, cmd):
        cmd += "\n"
        #print(cmd)
        self.ser.write(cmd.encode())

    def readBytes(self):
        if self.ser.in_waiting:
            line = self.ser.readline().decode("ascii")
            return line.split(":")
        return []

    def setMotorSpeed(self, speed0, speed1, speed2):
        self.__sendBytes("sd" + str(speed0) + ":" + str(speed1) + ":" + str(speed2))
        return self.waitForAnswer()

    def getMotorSpeed(self):
        self.__sendBytes("sg")

    def readInfrared(self):
        self.__sendBytes("i")

    def charge(self):
        self.__sendBytes("c")

    def kick(self):
        self.__sendBytes("k")

    def discharge(self):
        self.__sendBytes("e")

    def enableFailSafe(self):
        self.__sendBytes("f1")

    def disableFailSafe(self):
        self.__sendBytes("f0")

    def sendRFMessage(self, msg):
        self.__sendBytes("rf" + msg + "\n")

    def setThrowerSpeed(self, speed):
        self.__sendBytes("d" + str(speed))

    def enableFailDeadly(self):     #DON'T EVER USE THIS: IT WAS FUNNY UNTIL IT ACTUALLY FAILED DEADLY
        self.__sendBytes("fd")

    def closeSerial(self):
        if self.ser.isOpen():
            self.ser.close()

    def waitForAnswer(self):
        msg = self.readBytes()
        while not len(msg) > 0:
            msg = self.readBytes()
        return msg

    def setGrabberPosition(self, pos):
        self.__sendBytes("ss" + str(pos))