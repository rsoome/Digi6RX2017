# coding=utf-8

import numpy as np
import cv2
from datetime import datetime
import sys
from settings import SettingsHandler
from target import Target
from  movementLogic import MovementLogic
from imageProcessor import ImageHandler
from manualDrive import ManualDrive
from mbcomm import MBcomm

print("Running on Python " + sys.version)

settings = SettingsHandler.SettingsHandler("conf")

cap = cv2.VideoCapture(int(settings.getValue("camID")))
cap.set(cv2.CAP_PROP_FPS, 120)
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1080)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

textColor = (0, 0, 255)

framesCaptured = 0
totalTimeElapsed = 0
fps = 0

ball = Target.Target(None, None, "ball",
              np.array([int(x) for x in settings.getValue("ballHSVLower").split()]),
              np.array([int(x) for x in settings.getValue("ballHSVUpper").split()]))
basket = Target.Target(None, None, "basket",
              np.array([int(x) for x in settings.getValue("basketHSVLower").split()]),
              np.array([int(x) for x in settings.getValue("basketHSVUpper").split()]))

selectedTarget = ball

# If the mouse is clicked, update threshholds of the selected object
def onmouse(event, x, y, flags, params):  # Funktsioon, mis nupuvajutuse peale uuendab värviruumi piire
    if event == cv2.EVENT_LBUTTONUP:
        if selectedTarget is not None:
            selectedTarget.updateThresholds(hsv[y][x])

# Captures an image and returns the original frame and a filtered image.
# colorScheme - the filter to be applied
def capture(colorScheme):
    # Capture frame-by-frame
    ret, capturedFrame = cap.read()
    # Check whether the frame exists.
    if not ret:
        print("Cannot read the frame")
        return None, None

    img = cv2.cvtColor(capturedFrame, colorScheme)  # Pane pilt etteantud värviskeemi
    return capturedFrame, img


hsv = None

cv2.namedWindow('main')
cv2.namedWindow('ball_filtered')
cv2.namedWindow('gate_filtered')
cv2.setMouseCallback('main', onmouse)

mb = MBcomm.MBcomm(settings.getValue("mbLocation"), 115200)
#mb = None
move = MovementLogic.MovementLogic(mb)
imgHandler = ImageHandler.ImageHandler(bool(settings.getValue("multiThreading")))

#screen = curses.initscr()
#curses.cbreak()
#screen.keypad(1)

keyStroke = ''
#keyStroke = screen.getch()
while True:
    dt = datetime.now()
    #dt.microsecond
    start = float(str(dt).split()[1].split(":")[2]) * 1000000
    frame, hsv = capture(cv2.COLOR_BGR2HSV)  # Võta kaamerast pilt
    if frame is None:  # Kontroll, kas pilt on olemas
        print("Capture fucntion failed")
        break

    #hsv = blur(hsv)
    ballMask = cv2.inRange(hsv, ball.hsvLowerRange, ball.hsvUpperRange)  # Filtreeri välja soovitava värviga objekt
    ballMask = imgHandler.blur(ballMask)
    basketMask = cv2.inRange(hsv, basket.hsvLowerRange, basket.hsvUpperRange)
    basketMask = imgHandler.blur(basketMask)
    imgHandler.detect(frame, ballMask, 1000, 0, [1, 0, 2, 4, 3, 5, 7, 6, 8], ball)
    imgHandler.detect(frame, basketMask, 1000, 0, [7, 6, 8, 4, 3, 5, 1, 0, 2], basket)

    if ball.horizontalBounds is not None and ball.verticalBounds is not None:
        cv2.rectangle(frame, (ball.horizontalBounds[0], ball.verticalBounds[1]), (ball.horizontalBounds[1],
                                                                                ball.verticalBounds[0]), (255, 0, 0), 3)
    if basket.horizontalBounds is not None and basket.verticalBounds is not None:
        cv2.rectangle(frame, (basket.horizontalBounds[0], basket.verticalBounds[1]), (basket.horizontalBounds[1],
                                                                                        basket.verticalBounds[0]), (0, 255, 0), 3)

    if cv2.waitKey(1) & 0xFF == ord('e'):
        #        time.sleep(1)
        keyStroke = cv2.waitKey(100)
        if keyStroke & 0xFF == ord('q'):  # Nupu 'q' vajutuse peale välju programmist
            break
        #        time.sleep(1)
        if keyStroke & 0xFF == ord('b'):
            textColor = (0, 0, 255)
            selectedTarget = ball
            ball.resetThreshHolds()
            ball.resetBounds()

        #        time.sleep(1)
        if keyStroke & 0xFF == ord('k'):
            textColor = (255, 255, 0)
            selectedTarget = basket
            basket.resetThreshHolds()
            basket.resetBounds()

        if keyStroke & 0xFF == ord('m'):
            manual = ManualDrive.ManualDrive(move, int(settings.getValue("driveSpeed")), int(settings.getValue("turnSpeed")))
            manual.run()

    # print("Object size: " + str((ballHorizontalBounds[1] - ballHorizontalBounds[0]) * (ballVerticalBounds[1] - ballVerticalBounds[0])))
    cv2.putText(frame, "FPS: " + str(fps), (30, 30), cv2.FONT_HERSHEY_SIMPLEX,
                1, textColor, 1)

    # Display the resulting frame
    cv2.imshow('ball_filtered', ballMask)
    cv2.imshow('main', frame)
    cv2.imshow('gate_filtered', basketMask)

    dt = datetime.now()
    #dt.microsecond
    stop = float(str(dt).split()[1].split(":")[2]) * 1000000
    framesCaptured += 1
    totalTimeElapsed += stop - start
    if framesCaptured >= 60:
        fps = (round(framesCaptured / (totalTimeElapsed / 1000000), 0))
        framesCaptured = 0
        totalTimeElapsed = 0

settings.writeFromDictToFile()
# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
