import cv2
# Contins the game logic
# TODO: Implement
class GameLogic:

    def __init__(self, move, deltaFromMidPoint, moveSpeed, turnSpeed, imgHandler, frame, socketData):
        self.screenMidpoint = None
        self.move = move
        self.deltaFromMidPoint = deltaFromMidPoint
        self.moveSpeed = moveSpeed
        self.turnSpeed = turnSpeed
        self.imgHandler = imgHandler
        self.frame = frame
        self.initializeValues()
        self.socketData = socketData

    def turnToTarget(self, scanOrder, target):
        if target.horizontalMidPoint != None:
            while (target.horizontalMidPoint != None and not self.checkHorizontalAlginment(target)):
                if not self.socketData.gameStarted:
                    break
                self.updateTargetCoordinates(scanOrder, target)
                if target.horizontalMidPoint != None:
                    if target.horizontalMidPoint > self.screenMidpoint:
                        self.move.rotate(self.turnSpeed)
                    elif target.horizontalMidPoint < self.screenMidpoint:
                        self.move.rotate(-self.turnSpeed)

    def moveToTarget(self, scanOrder, target):
        self.updateTargetCoordinates(scanOrder, target)
        print(target.horizontalMidPoint)

        if target.horizontalMidPoint != None:
            self.turnToTarget(scanOrder, target)
            while (not self.checkVerticalAlignment()):
                if not self.socketData.gameStarted:
                    break
                self.updateTargetCoordinates(scanOrder, target)
                self.move.drive(self.moveSpeed, 0)
            #start ballroller
            self.move.drive(self.moveSpeed, 0)

    def updateTargetCoordinates(self, scanOrder, target):
        self.frame.capture(cv2.COLOR_BGR2HSV)
        self.imgHandler.generateMask(target, self.frame.filteredImg)
        self.imgHandler.detect(None, target.mask, 1000, 0, scanOrder, target)

    def lookForBall(self, scanOrder, target):
        i = 0
        while target.horizontalMidPoint == None or i < 10:
            if not self.socketData.gameStarted:
                break
            self.updateTargetCoordinates(scanOrder, target)
            self.move.rotate(self.turnSpeed)
            i += 1

    def run(self, scanOrder, target):
        while(self.socketData.gameStarted):
            if(not self.checkVerticalAlignment() and self.checkHorizontalAlginment()):
                self.lookForBall(scanOrder, target)
                #print(target.horizontalMidPoint)
                self.turnToTarget(scanOrder, target)
                #print(target.horizontalMidPoint)
                self.moveToTarget(scanOrder, target)
                #print(target.verticalMidPoint)
                #print("---------------------")
        self.move.rotate(0)


    def initializeValues(self):
        self.frame.capture(cv2.COLOR_BGR2HSV)
        self.screenMidpoint = self.frame.width//2

    def checkHorizontalAlginment(self, target):

        if (target.horizontalMidPoint != None and (target.horizontalMidPoint > self.screenMidpoint + self.deltaFromMidPoint
            or target.horizontalMidPoint < self.screenMidpoint - self.deltaFromMidPoint)):

            return False

        return True

    def checkVerticalAlignment(self, target):

        if(target.verticalMidPoint == None):
            return False

        if(target.verticalMidPoint != None and target.verticalMidPoint < 460):
            return False

        return True

