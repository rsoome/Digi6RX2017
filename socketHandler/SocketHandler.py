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

    def __init__(self, socketData, ball, basket, fps, frame, blackLine):
        self.socketData = socketData
        self.ball = ball
        self.basket = basket
        self.fps = fps
        self.frame = frame
        self.values = dict()
        self.acknowledged = False
        self.blackLine = blackLine

    def updateData(self):

        #cv2.imencode(".jpg", self.socketData.img)[1]
        #print(type(self.frame.capturedFrame.shape()))
        if self.frame.capturedFrame is not None:
            self.socketData.imgDimensions = self.frame.capturedFrame.shape
            self.socketData.img = self.frame.bw

            if self.ball.contours is not None:
                cv2.drawContours(self.socketData.img, self.ball.contours, -1, [255, 0, 0])

            if self.basket.contours is not None:
                cv2.drawContours(self.socketData.img, self.basket.contours, -1, [0, 255, 0])

            if self.blackLine.contours is not None:
                cv2.drawContours(self.socketData.img, self.blackLine.contours, -1, [0,0,255])

        self.socketData.ballHorizontalBounds = self.ball.horizontalBounds
        self.socketData.ballVerticalBounds = self.ball.verticalBounds
        self.socketData.basketHorizontalBounds = self.basket.horizontalBounds
        self.socketData.basketVerticalBounds = self.basket.verticalBounds

    def updateValues(self):
        self.values["imgDimensions"] = self.socketData.imgDimensions
        self.values["img"] = self.socketData.img
        self.values["basketDimensions"] = self.socketData.basketDimensions
        self.values["basketMask"] = self.socketData.basketMask
        self.values["ballMask"] = self.socketData.ballMask
        self.values["ballDimensions"] = self.socketData.ballDimensions
        self.values["fps"] = self.socketData.fps
        self.values["ballHorizontalBounds"] = self.socketData.ballHorizontalBounds
        self.values["ballVerticalBounds"] = self.socketData.ballVerticalBounds
        self.values["basketHorizontalBounds"] = self.socketData.basketHorizontalBounds
        self.values["basketVerticalBounds"] = self.socketData.basketVerticalBounds

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
        self.servSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.servSock.bind((host, self.servPort))  # Bind to the port
        self.servSock.listen(1)  # Now wait for client connection.
        try:
            closedByClient = self.streamData(None, None)

            if closedByClient:
                self.servSock.close()

        except Exception as e:
            print("An error occured, closing connections.")
            self.servSock.close()
            raise e

    def streamData(self, conn, addr):
        while True:
            self.updateData()
            try:
                if conn == None:
                    self.servSock.settimeout(0.1)
                    conn, addr = self.servSock.accept()
                    time.sleep(1)

                    messageSent = self.sendMessage({"check": ""}, conn, 0.1)
                    if messageSent:
                        self.waitForAck(conn)

                else:

                    messageSent = self.sendMessage({"check": ""}, conn, 0.001)

                    if messageSent:
                        self.waitForAck(conn)
                        self.updateValues()
                        messageSent = self.sendMessage(self.values, conn, 4)

                    messages = self.listen(conn, 0.1)

                    if messages != None:
                        self.handleMessages(messages, conn)

                    if self.socketData.stop:
                        conn.close()
                        self.socketData.socketClosed = True
                        return True

                    if self.socketData.clientDC:
                        conn.close()
                        return False

            except socket.timeout:
                #print("Socket timed out")
                pass

            except socket.error as e:
                print("Client socket closed.")
                if e.errno != errno.EPIPE and e.errno != errno.ECONNABORTED and e.errno != errno.ECONNRESET:
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
                messages = self.listen(sock, 0.3)
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
                self.socketData.stop = messages[key]

            if key == "ballSelected":
                self.socketData.ballSelected = messages[key]
                self.socketData.basketSelected = not messages[key]

            if key == "ballHorizontalBounds":
                self.socketData.ballHorizontalBounds = messages[key]

            if key == "ballVerticalBounds":
                self.socketData.ballVerticalBounds = messages[key]

            if key == "basketSelected":
                self.socketData.ballSelected = not messages[key]
                self.socketData.basketSelected = messages[key]

            if key == "basketHorizontalBounds":
                self.socketData.basketHorizontalBounds = messages[key]

            if key == "basketVerticalBounds":
                self.socketData.basketVerticalBounds = messages[key]

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

            if key == "refreshConf":
                self.socketData.refreshConf = bool(messages[key])

            if key == "updateConf":
                self.socketData.updateConf = bool(messages[key])

            if key == "DC":
                self.socketData.clientDC = bool(messages[key])

            if key == "setMagneta":
                self.socketData.setMagneta = bool(messages[key])

            if key == "setBlue":
                self.socketData.setBlue = bool(messages[key])

