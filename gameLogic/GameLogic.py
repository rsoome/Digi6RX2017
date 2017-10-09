
# Contins the game logic
# TODO: Implement
class GameLogic:

    def __init__(self, target, screenMidpoint, move, deltaFromMidPoint, moveSpeed, turnSpeed, imgHandler):

        #mainImg, target, objectMinSize, imageMinArea, scanOrder, obj
        self.target = target
        self.screenMidpoint = screenMidpoint
        self.move = move
        self.deltaFromMidPoint = deltaFromMidPoint
        self.moveSpeed = moveSpeed
        self.turnSpeed = turnSpeed
        self.imgHandler = imgHandler

    def turnToBall(self):
        if self.target.midPoint > self.screenMidpoint:
            while self.target.midPoint >= self.screenMidpoint + self.deltaFromMidPoint:
                self.move.rotate(self.turnSpeed)

