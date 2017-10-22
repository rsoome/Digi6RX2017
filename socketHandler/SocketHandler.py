import socket

import sys
import traceback

import cv2
import errno

import numpy as np
import time
import pickle
import zlib


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
            self.socketData.img = self.frame.bw

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

    def listen(self, conn, t):

        #print("**")
        if conn == None:
            return None

        conn.settimeout(t)

        data = b""
        try:
            packet = conn.recv(4096)
            while packet:
                try:
                    #print(len(packet))
                    data += packet
                    packet = conn.recv(4096)
                except socket.timeout:
                    #print("Listening timed out")
                    break

            #print(data)
            if self.socketData.stop or len(data) < 1:
                return None
            decompressed = zlib.decompress(data, 0)
            readData = pickle.loads(decompressed)
            return readData

        except socket.timeout:
            #print("Listening timed out")
            return None

        except pickle.UnpicklingError as e:
            print(e)

        except zlib.error as e:
            print(e)


    def initServ(self):
        host = ""
        self.servSock = socket.socket()  # Create a socket object
        self.servHost = socket.gethostname()  # Get local machine name
        self.servPort = 12345  # Reserve a port for your service.
        self.servSock.bind((host, self.servPort))  # Bind to the port
        self.servSock.listen(1)  # Now wait for client connection.
        try:
            self.streamData(None, None)
        except Exception as e:
            print("An error occured, closing connections.")
            self.servSock.close()
            raise e

    def streamData(self, conn, addr):
        while True:
            print("Updating data")
            self.updateData()
            print("Data updated")
            try:
                if conn == None:
                    self.servSock.settimeout(0.1)
                    conn, addr = self.servSock.accept()

                    messageSent = self.sendMessage({"check": ""}, conn, 0.1)
                    if messageSent:
                        self.waitForAck(conn)

                    print("Connection established to: " + str(addr))
                    #time.sleep(0.1)

                else:

                    #print(self.values)
                    print("Checking connection")
                    messageSent = self.sendMessage({"check": ""}, conn, 0.001)

                    if messageSent:
                        self.waitForAck(conn)
                        print("Connection OK, updating values")
                        self.updateValues()
                        print("Values updated, sending.")
                        messageSent = self.sendMessage(self.values, conn, 4)

                    else:
                        print("Sending message timed out.")

                    print("Listening for incoming messages")
                    messages = self.listen(conn, 0.1)

                    if messages != None:
                        print("Received messages. Handling")
                        self.handleMessages(messages, conn)
                        print("Messages handled.")

                    if self.socketData.stop:
                        conn.close()
                        self.socketData.socketClosed = True
                        return

            except socket.timeout:
                #print("Socket timed out")
                pass

            except socket.error as e:
                print("Client socket closed.")
                if e.errno != errno.EPIPE:
                    raise
                try:
                    conn.close()
                except:
                    pass
                conn = None
                addr = None

            #time.sleep(0.03)

    def waitForAck(self, conn):
        timeOutCounter = 0
        while  not self.acknowledged and timeOutCounter <= 10:
            ret = self.listen(conn, 0.1)
            #print(ret)
            if ret is not None:
                self.handleMessages(ret, conn)
            else:
                timeOutCounter += 1
        self.acknowledged = False

    def initClient(self, host, port):
        self.clientSock = socket.socket()
        self.clientSock.connect((host, port))
        try:
            self.runClient(self.clientSock)
        except Exception as e:
            print("Client socket failed. Closing Socket.")
            print(e)
            messageSent = self.sendMessage({"stop": True}, self.clientSock, 0.05)
            self.socketData.stop = True
            self.clientSock.close()

    def runClient(self, sock):
        #sock.settimeout(2)
        while True:
            #print("*")
            try:
                if self.socketData.stop:
                    break
                messages = self.listen(sock, 0.1)
                if messages != None:
                    self.handleMessages(messages, sock)
                #time.sleep(0.03)
            except socket.timeout:
                print("Listening timed out.")
                pass
        sock.close()

    def sendMessage(self, msg, conn, timeout):

        conn.settimeout(timeout)
        pickled = pickle.dumps(msg)
        compressed = zlib.compress(pickled, 1)

        try:
            #print(len(pickled))
            #print(msg)
            conn.sendall(compressed)
            return True

        except socket.timeout as e:
            return ("Sending message timed out.")
            return False


    def handleMessages(self, messages, sock):

        for key in messages:

            #print(key)

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
                #print("img")
                #print(messages[key])
                #print("img recv")
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

            if key == "check":
                messageSent = self.sendMessage({"ack" : True}, sock, 0.1)

