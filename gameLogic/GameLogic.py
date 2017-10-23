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
        self.verticalStopBound = 400

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
            self.move.rotate(0)

    def moveToTarget(self, scanOrder, target):
        self.updateTargetCoordinates(scanOrder, target)
        print(target.horizontalMidPoint)

        if target.horizontalMidPoint != None:
            self.turnToTarget(scanOrder, target)
            while (not self.checkVerticalAlignment(target)):

                if target.horizontalMidPoint != None and not self.checkHorizontalAlginment(target):
                    break

                if not self.socketData.gameStarted:
                    break

                self.updateTargetCoordinates(scanOrder, target)
                self.move.drive(self.moveSpeed, 0)
            #start ballroller
            self.move.rotate(0)

    def updateTargetCoordinates(self, scanOrder, target):
        self.frame.capture(cv2.COLOR_BGR2HSV)
        self.imgHandler.generateMask(target, self.frame.filteredImg)
        self.imgHandler.detect(None, target.mask, 1000, 0, scanOrder, target)

    def lookForBall(self, scanOrder, target):
        self.updateTargetCoordinates(scanOrder, target)
        i = 0
        while i < 400:
            if not self.socketData.gameStarted :
                break
            self.updateTargetCoordinates(scanOrder, target)
            self.move.rotate(self.turnSpeed)
            i += 1
            print("****")
            print(target.horizontalMidPoint)
            if target.horizontalMidPoint != None:
                return True

        return False

    def run(self, scanOrder, target):
        while(self.socketData.gameStarted):
            if(not (self.checkVerticalAlignment(target) and self.checkHorizontalAlginment(target))):
                targetFound = self.lookForBall(scanOrder, target)
                if not targetFound:
                    if not self.socketData.gameStarted:
                        break
                    print("Relocating")
                    for i in range(5000):
                        self.move.drive(self.moveSpeed, 0)
                self.turnToTarget(scanOrder, target)
                self.moveToTarget(scanOrder, target)

            else:
                self.updateTargetCoordinates(scanOrder, target)
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

        if(target.verticalMidPoint != None and target.verticalMidPoint < self.verticalStopBound):
            return False

        return True

