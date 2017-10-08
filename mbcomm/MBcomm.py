import serial

class MBcomm:

    def __init__(self, target, baud):
        self.ser = serial.Serial(port=target, baudrate=baud, timeout=0.8)

    def __sendByte(self, cmd):
        if not self.ser.isOpen():
            self.ser.open()
        cmd += "\n"
        print(cmd)
        self.ser.write(cmd.encode())
        if self.ser.isOpen():
            self.ser.close()

    def __readBytes(self):
        if not self.ser.isOpen():
            self.ser.open()
        line = self.ser.readline().decode("ascii")
        if self.ser.isOpen():
            self.ser.close()
        return line

    def setMotorSpeed(self, speed0, speed1, speed2):
        self.__sendByte("sd" + str(speed0) + ":" + str(speed1) + ":" + str(speed2))

    def getMotorSpeed(self):
        self.__sendByte("sg")
        return self.__readBytes()

    def readInfrared(self):
        self.__sendByte("i")
        return self.__readBytes()

    def charge(self):
        self.__sendByte("c")

    def kick(self):
        self.__sendByte("k")

    def discharge(self):
        self.__sendByte("e")

    def enableFailSafe(self):
        self.__sendByte("f")