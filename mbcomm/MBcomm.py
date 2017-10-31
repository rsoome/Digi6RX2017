import serial

class MBcomm:

    def __init__(self, target, baud):
        self.ser = serial.Serial(port=target, baudrate=baud, timeout=0.8)
        if not self.ser.isOpen():
            self.ser.open()
            self.THROWER_MAXSPEED = 2000

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

    def startThrower(self, speed):
        self.__sendBytes("cg")
        self.__sendBytes("d" + str(speed))

    def enableFailDeadly(self):     #DON'T EVER USE THIS
        self.sendBytes("fd")

    def closeSerial(self):
        if self.ser.isOpen():
            self.ser.close()

    def waitForAnswer(self):
        msg = self.readBytes()
        while not len(msg) > 0:
            msg = self.readBytes()
        return msg