import serial
import time

from timer import Timer


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
        self.GRABBER_CARRY_POSITION = self.GRABBER_MAX_POSITION - 400
        self.GRABBER_THROW_POSITION = self.GRABBER_MIN_POSITION
        self.GRABBER_OPEN_POSITION = self.GRABBER_MAX_POSITION - 100
        self.values = dict()
        self.sendTimer = Timer.Timer()
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
        #print("Speed0: " + str(speed0))
        #print("Speed1: " + str(speed1))
        #print("Speed2: " + str(speed2))
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
        if len(self.values) > 0:
            #print("-----")
            for key in self.values:
                #print(key + self.values[key])
                self.__sendBytes(key + self.values[key])
                time.sleep(0.05)
            #print("------")
            self.values = dict()
            self.sendTimer.reset()

    def sendingTime(self):
        if self.sendTimer.getTimePassed() >= 1000/self.SENDFREQ:
            self.sendTimer.reset()
            return True
        return False
