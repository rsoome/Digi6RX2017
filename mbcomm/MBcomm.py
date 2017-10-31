import serial

class MBcomm:

    def __init__(self, target, baud):
        self.ser = serial.Serial(port=target, baudrate=baud, timeout=0.8)
        if not self.ser.isOpen():
            self.ser.open()

    def __sendByte(self, cmd):
        cmd += "\n"
        #print(cmd)
        self.ser.write(cmd.encode())

    def readBytes(self):
        if self.ser.in_waiting:
            line = self.ser.readline().decode("ascii")
            return line.split(":")
        return []

    def setMotorSpeed(self, speed0, speed1, speed2):
        self.__sendByte("sd" + str(speed0) + ":" + str(speed1) + ":" + str(speed2))

    def getMotorSpeed(self):
        self.__sendByte("sg")

    def readInfrared(self):
        self.__sendByte("i")

    def charge(self):
        self.__sendByte("c")

    def kick(self):
        self.__sendByte("k")

    def discharge(self):
        self.__sendByte("e")

    def enableFailSafe(self):
        self.__sendByte("f")

    def sendRFMessage(self, msg):
        self.__sendByte("rf" + msg + "\n")

    def closeSerial(self):
        if self.ser.isOpen():
            self.ser.close()