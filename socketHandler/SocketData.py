class SocketData:

    def __init__(self):
        self.stop = False
        self.ballSelected = True
        self.basketSelected = False
        self.blackLineSelected = False
        self.manualDrive = False
        self.gameStarted = False
        self.img = None
        self.ballMask = None
        self.basketMask = None
        self.fps = 0
        self.socketClosed = False
        self.ballHorizontalBounds = None
        self.ballVerticalBounds = None
        self.basketHorizontalBounds = None
        self.basketVerticalBounds = None
        self.blacklineHorizontalBounds = None
        self.blackLineVerticalBounds = None
        self.resetBall = False
        self.resetBasket = False
        self.resetBlackLine = False
        self.manualDrive = False
        self.imgDimensions = None
        self.basketDimensions = None
        self.ballDimensions = None
        self.updateThresholds = False
        self.mouseX = -1
        self.mouseY = -1
        self.refreshConf = False
        self.updateConf = False
        self.clientDC = False
        self.setMagneta = False
        self.setBlue = False
        self.blackLineSelected = False

    def setAll(self, ballSelected, manualDrive, gameStarted, img, ballMask, basketMask,
               fps, ballHorizontalBounds, ballVerticalBounds, basketHorizontalBounds, basketVerticalBounds):
        self.ballSelected = ballSelected
        self.basketSelected = not ballSelected
        self.manualDrive = manualDrive
        self.gameStarted = gameStarted
        self.img = img
        self.ballMask = ballMask
        self.basketMask = basketMask
        self.fps = fps
        self.ballHorizontalBounds = ballHorizontalBounds
        self.ballVerticalBounds = ballVerticalBounds
        self.basketHorizontalBounds = basketHorizontalBounds
        self.basketVerticalBounds = basketVerticalBounds