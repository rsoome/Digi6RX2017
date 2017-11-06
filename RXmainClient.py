# coding=utf-8

import sys

import time

from settings import SettingsHandler
from windowHandler import WindowHandler
from socketHandler import SocketHandler
from socketHandler import SocketData
import threading
import socket

print("Running on Python " + sys.version)

settings = SettingsHandler.SettingsHandler("conf")

textColor = (0, 0, 255)

framesCaptured = 0
totalTimeElapsed = 0
fpsStatus = "0"
socketData = SocketData.SocketData()
socketHandler = SocketHandler.SocketHandler(socketData, None, None, None, None)
window = WindowHandler.WindowHandler(socketData, socketHandler)
hostname = "Digi6"

host = "127.0.0.1"

try:
    host = socket.gethostbyname(hostname)
except:
    print("Cannot connect to host " + hostname)

t = threading.Thread(target=socketHandler.initClient, args=(host, 12345))
t.start()

while True:

    frame = socketData.img
    if frame is None:  # Kontroll, kas pilt on olemas
        fpsStatus = "No image to show"
    else:
        fpsStatus = socketData.fps

    window.fps = fpsStatus
    window.showImage()
    #print(window.halt)
    if socketData.stop:
        break
    time.sleep(0.1)

settings.writeFromDictToFile()
