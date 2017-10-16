import cv2
#from manualDrive import ManualDrive
import sys

class WindowHandler:

    def __init__(self, frameCapture, ball, basket, driveSpeed, turnSpeed, move, game, scanOrder):
        self.game = game
        cv2.namedWindow('main')
        cv2.namedWindow('ball_filtered')
        cv2.namedWindow('gate_filtered')
        cv2.setMouseCallback('main', self.onmouse)
        self.selectedTarget = ball
        self.frame = frameCapture
        self.fps = 0
        self.ball = ball
        self.basket = basket
        self.driveSpeed = driveSpeed
        self.turnSpeed = turnSpeed
        self.move = move
        self.textColor = (0, 0, 255)
        self.halt = False
        self.scanOrder = scanOrder

    # If the mouse is clicked, update threshholds of the selected object
    def onmouse(self, event, x, y, flags, params):  # Funktsioon, mis nupuvajutuse peale uuendab värviruumi piire
        if event == cv2.EVENT_LBUTTONUP:
            if self.selectedTarget is not None:
                self.selectedTarget.updateThresholds(self.frame.filteredImg[y][x])

    def showImage(self):
        if self.ball.horizontalBounds is not None and self.ball.verticalBounds is not None:
            print(self.ball.verticalMidPoint)
            cv2.rectangle(self.frame.capturedFrame, (self.ball.horizontalBounds[0], self.ball.verticalBounds[1]),
                          (self.ball.horizontalBounds[1], self.ball.verticalBounds[0]), (255, 0, 0), 3)

        if self.basket.horizontalBounds is not None and self.basket.verticalBounds is not None:
            cv2.rectangle(self.frame.capturedFrame, (self.basket.horizontalBounds[0], self.basket.verticalBounds[1]),
                          (self.basket.horizontalBounds[1], self.basket.verticalBounds[0]), (0, 255, 0), 3)

        if cv2.waitKey(1) & 0xFF == ord('e'):
            #        time.sleep(1)
            keyStroke = cv2.waitKey(100)
            if keyStroke & 0xFF == ord('q'):  # Nupu 'q' vajutuse peale välju programmist
                self.closeWindows()
            # time.sleep(1)
            if keyStroke & 0xFF == ord('b'):
                self.textColor = (0, 0, 255)
                self.selectedTarget = self.ball
                self.ball.resetThreshHolds()
                self.ball.resetBounds()

            # time.sleep(1)
            if keyStroke & 0xFF == ord('k'):
                self.textColor = (255, 255, 0)
                self.selectedTarget = self.basket
                self.basket.resetThreshHolds()
                self.basket.resetBounds()

            if keyStroke & 0xFF == ord('m'):
                manual = ManualDrive.ManualDrive(self.move, self.driveSpeed, self.turnSpeed)
                manual.run()

            if keyStroke & 0xFF == ord('g'):
                self.game.lookForBall(self.scanOrder, self.ball)
                self.game.moveToTarget(self.scanOrder, self.ball)

        # print("Object size: " + str((ballHorizontalBounds[1] - ballHorizontalBounds[0]) * (ballVerticalBounds[1] - ballVerticalBounds[0])))
        cv2.putText(self.frame.capturedFrame, "FPS: " + str(self.fps), (30, 30), cv2.FONT_HERSHEY_SIMPLEX,
                    1, self.textColor, 1)

        # Display the resulting frame
        cv2.imshow('ball_filtered', self.ball.mask)
        cv2.imshow('main', self.frame.capturedFrame)
        cv2.imshow('gate_filtered', self.basket.mask)

    def closeWindows(self):
        cv2.destroyAllWindows()
        self.halt = True
