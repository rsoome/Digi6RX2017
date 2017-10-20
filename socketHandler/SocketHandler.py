import socket

import sys
import cv2

import numpy as np
import time
import pickle


class SocketHandler:

    def __init__(self, socketData, ball, basket, fps, frame):
        self.socketData = socketData
        self.ball = ball
        self.basket = basket
        self.fps = fps
        self.frame = frame
        self.values = dict()
        self.acknowledged = False

    def updateData(self):

        #cv2.imencode(".jpg", self.socketData.img)[1]
        #print(type(self.frame.capturedFrame.shape()))
        if self.frame.capturedFrame is not None:
            self.socketData.imgDimensions = self.frame.capturedFrame.shape
            self.socketData.img = self.frame.capturedFrame

        if self.ball.mask is not None:
            self.socketData.ballDimensions = self.ball.mask.shape
            self.socketData.ballMask = self.ball.mask

        if self.basket.mask is not None:
            self.socketData.basketDimensions = self.basket.mask.shape
            self.socketData.basketMask = self.basket.mask

    def updateValues(self):
        self.values["imgDimensions"] = self.socketData.imgDimensions
        self.values["img"] = self.socketData.img
        self.values["basketDimensions"] = self.socketData.basketDimensions
        self.values["basketMask"] = self.socketData.basketMask
        self.values["ballMask"] = self.socketData.ballMask
        self.values["ballDimensions"] = self.socketData.ballDimensions
        self.values["fps"] = self.socketData.fps

    def listen(self, conn):

        #print("**")
        if conn == None:
            return None

        conn.settimeout(0.05)
        packetsReceived = False
        readData = None

        data = b""
        try:
            packet = conn.recv(4096)
            if packet:
                packetsReceived = True
            while packet:
                #print(len(packet))
                data += packet
                packet = conn.recv(4096)

            #print(data)
            if self.socketData.stop:
                return None
            readData = pickle.loads(data)
            return readData

        except socket.timeout:
            if packetsReceived:
                if self.socketData.stop:
                    return None
                readData = pickle.loads(data)
                #print(readData)
                return readData
            return None


    def initServ(self):
        host = ""
        self.servSock = socket.socket()  # Create a socket object
        self.servHost = socket.gethostname()  # Get local machine name
        self.servPort = 12345  # Reserve a port for your service.
        self.servSock.bind((host, self.servPort))  # Bind to the port
        self.servSock.listen(1)  # Now wait for client connection.
        self.streamData(None, None)

    def streamData(self, conn, addr):
        while True:
            self.updateData()
            if conn == None:
                try:
                    self.servSock.settimeout(0.5)
                    conn, addr = self.servSock.accept()
                    print("Connection established to: " + str(addr))
                except socket.timeout:
                    conn = None
                    addr = None

            messages = self.listen(conn)

            if messages != None:
                #print("Received messages.")
                self.handleMessages(messages)

            if self.socketData.stop:
                self.socketData.socketClosed = True
                break

            self.updateValues()
            #print(self.values["img"])

            if conn != None:
                #print(self.values)
                self.sendMessage(self.values, conn)
                self.waitForAck(conn)


            time.sleep(0.03)

        try:
            conn.close
        except:
            print("Cannot close conn if conn is None.")

    def waitForAck(self, conn):

        while  not self.acknowledged:
            ret = self.listen(conn)
            #print(ret)
            if ret is not None:
                self.handleMessages(ret)
        self.acknowledged = False

    #def createNumpyArrayFromString(self, s):
    #    return np.fromstring(s, np.int8) - 48

    def initClient(self, host, port):
        self.clientSock = socket.socket()
        self.clientSock.connect((host, port))
        self.runClient(self.clientSock)

    def runClient(self, sock):
        sock.settimeout(0.5)
        while True:
            #print("*")
            if self.socketData.stop:
                break
            messages = self.listen(sock)
            if messages != None:
                self.handleMessages(messages)
                self.values["ack"] = True
                self.sendMessage(self.values, sock)
            time.sleep(0.03)
        sock.close()

    def sendMessage(self, msg, conn):
        #print(msg)
        conn.sendall(pickle.dumps(msg))


    def handleMessages(self, messages):

        for key in messages:

            if key == "stop":
                sys.exit(0)

            if key == "ballSelected":
                self.socketData.ballSelected = messages[key]
                self.socketData.basketSelected = not messages[key]

            if key == "basketSelected":
                self.socketData.ballSelected = not messages[key]
                self.socketData.basketSelected = messages[key]

            if key == "manualDrive":
                self.socketData.manualDrive = messages[key]

            if key == "gameStarted":
                self.socketData.gameStarted = messages[key]

            if key == "img":
                #print(messages[key])
                self.socketData.img = messages[key]

            if key == "ballMask":
                #print("Received ball mask")
                self.socketData.ballMask = messages[key]
                #print(self.socketData.ballMask)

            if key == "basketMask":
                #print("Received basket mask")
                self.socketData.basketMask = messages[key]

            if key == "fps":
                self.socketData.fps = messages[key]

            if key == "resetBall":
                self.socketData.resetBall = messages[key]

            if key == "resetBasket":
                self.socketData.resetBasket = messages[key]

            if key == "manualDrive":
                self.socketData.manualDrive = messages[key]

            if key == "updateThresholds":
                self.socketData.updateThresholds = messages[key]

            if key == "mouseX":
                self.socketData.mouseX = messages[key]

            if key == "mouseY":
                self.socketData.mouseY = messages[key]

            if key == "ack":
                self.acknowledged = messages[key]

