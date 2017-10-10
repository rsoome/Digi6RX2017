import cv2
# Contins the game logic
# TODO: Implement
class GameLogic:

    def __init__(self, move, deltaFromMidPoint, moveSpeed, turnSpeed, imgHandler, frame):
        self.screenMidpoint = None
        self.move = move
        self.deltaFromMidPoint = deltaFromMidPoint
        self.moveSpeed = moveSpeed
        self.turnSpeed = turnSpeed
        self.imgHandler = imgHandler
        self.frame = frame
        self.initializeValues()

    def turnToTarget(self, scanOrder, target):
        if target.midPoint != None:
            if target.midPoint > self.screenMidpoint:
                while target.midPoint > self.screenMidpoint + self.deltaFromMidPoint:
                    print("Target midpoint: " + str(target.midPoint))
                    print("Screen midpoint: " + str(self.screenMidpoint))
                    self.frame.capture(cv2.COLOR_BGR2HSV)
                    self.imgHandler.generateMask(target, self.frame.filteredImg)
                    self.imgHandler.detect(None, target.mask, 1000, 0, scanOrder, target)
                    self.move.rotate(self.turnSpeed)
            else:
                while target.midPoint < self.screenMidpoint + self.deltaFromMidPoint:
                    self.frame.capture(cv2.COLOR_BGR2HSV)
                    self.imgHandler.generateMask(target, self.frame.filteredImg)
                    self.imgHandler.detect(None, target.mask, 1000, 0, scanOrder, target)
                    self.move.rotate(-self.turnSpeed)

    def moveToTarget(self, scanOrder, target):
        if target.midPoint != None:
            self.turnToTarget(scanOrder, target)
            while target.midPoint != None:
                self.frame.capture(cv2.COLOR_BGR2HSV)
                self.imgHandler.generateMask(target, self.frame.filteredImg)
                self.imgHandler.detect(None, target.mask, 1000, 0, scanOrder, target)
                self.move.drive(self.moveSpeed, -60)

    def initializeValues(self):
        self.frame.capture(cv2.COLOR_BGR2HSV)
        self.screenMidpoint = self.frame.width//2


