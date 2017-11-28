import serial
import time

from timer import Timer


class MBcomm:

    def __init__(self, target, baud):
        self.ser = serial.Serial(port=target, baudrate=baud, timeout=0.8)
        self.values = dict()
        self.sendTimer = Timer.Timer()
        self.sendTimer.startTimer()
        self.SENDFREQ = 240
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
        self.setValue("sd", str(speed0) + ":" + str(speed1) + ":" + str(speed2))

    def getMotorSpeed(self):
        self.setValue("sg", "")

    def readInfrared(self):
        self.setValue("i", "")

    def enableFailSafe(self):
        self.setValue("f1","")

    def disableFailSafe(self):
        self.setValue("f0", "")

    def sendRFMessage(self, msg):
        self.setValue("rf", msg + "\n")

    def setThrowerSpeed(self, speed):
        self.setValue("d", str(speed))

    def enableFailDeadly(self):     #DON'T EVER USE THIS: IT WAS FUNNY UNTIL IT ACTUALLY FAILED DEADLY
        self.setValue("fd", "")

    def closeSerial(self):
        if self.ser.isOpen():
            self.ser.close()

    def waitForAnswer(self):
        msg = self.readBytes()
        for i in range(1000000):
            if len(msg) > 0:
                return msg
            msg = self.readBytes()
        print("Mainboard crashed.")
        return msg

    def setGrabberPosition(self, pos):
        self.setValue("ss", str(pos))

    def clearMBbuf(self):
        self.setValue("cb", "")

    def setValue(self, node, value):
        self.values[node] = value

    def sendValues(self):
        print("Values length: ", len(self.values))
        print("sendTimer: ", self.sendTimer.getTimePassed())
        print("sendingTime: ", self.sendingTime())
        if len(self.values) > 0 and self.sendingTime():
            #print("-----")
            for key in self.values:
                #print(key + self.values[key])
                self.__sendBytes(key + self.values[key])
                time.sleep(0.05)
            #print("------")
            self.values = dict()
            self.sendTimer.reset()
            return True
        return False

    def sendingTime(self):
        if self.sendTimer.getTimePassed() >= 1000/self.SENDFREQ:
            self.sendTimer.reset()
            return True
        return False
