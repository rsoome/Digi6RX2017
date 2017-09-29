import numpy as np
import cv2

camID = 0   #Kaamera ID
cap = cv2.VideoCapture(camID)
ballLowerRange = np.array([255, 255, 255]) #HSV värviruumi alumine piir, hilisemaks filtreerimiseks
ballUpperRange = np.array([0, 0, 0]) #HSV värviruumi ülemine piir, hilisemaks filtreerimiseks

hsv = None

def onmouse(event, x, y, flags, params): #Funktsioon, mis nupuvajutuse peale uuendab värviruumi piire
    if event == cv2.EVENT_LBUTTONUP:
        hsvArr = (hsv[y][x])
        for i in range(3):
            if hsvArr[i] < ballLowerRange[i]:
                ballLowerRange[i] = hsvArr[i] #Kui väärtus on väiksem ,uuenda alumist piiri
            if hsvArr[i] > ballUpperRange[i]:
                ballUpperRange[i] = hsvArr[i] #Kui väärtus on suurem, uuenda ülemist piiri

def capture(colorScheme):   #Teeb pildi ja tagastab selle etteantud värviskeemis
    # Capture frame-by-frame
    ret, frame = cap.read()
    if(not ret):    #Kontroll, kas kaader eksisteerib
        print("Cannot read the frame")
        return frame

    img = cv2.cvtColor(frame, colorScheme) #Pane pilt etteantud värviskeemi
    return img

def blur(img):
    kernel = np.ones((30,30), np.uint8)  #//TODO: Find values to put in the kernel
    dilation = cv2.dilate(img, kernel, 1) #Udusta pilti //TODO: püüda dilationist ja erotionist paremini aru saada
    kernel = np.ones((10,10), np.uint8)   #//TODO: Find values to put in the kernel
    erotion = cv2.erode(dilation, kernel, 1) #Teravda pilti
    return erotion

def scanPixelsForObject(object, height, width, minSize):
    horizontalBounds = np.array([width,0])
    verticalBounds = np.array([height,0])
    for i in range(height):
        for j in range(width):
            if(object[i][j]!= 0 and (i < verticalBounds[0] or i > verticalBounds[1])
               and (j < horizontalBounds[0] or j > horizontalBounds[1])):
                findBounds(object, height, width, horizontalBounds, verticalBounds, i, j)
                objectWidth = (horizontalBounds[1] - horizontalBounds[0])
                objectHeight = (verticalBounds[1] - verticalBounds[0])
                if(objectWidth * objectHeight >= minSize):
                    return True, horizontalBounds, verticalBounds


    return False, horizontalBounds, verticalBounds


def findBounds(object, height, width, horizontalBounds, verticalBounds, i, j):
    verticalBounds[0] = i
    for k in range(i, height):
        if object[k][j] == 0 or k == height - 1:
            verticalBounds[1] = k
            break
    midpoint = verticalBounds[0] + (verticalBounds[1] - verticalBounds[0]) // 2
    k = j
    while (object[midpoint][k] != 0 and k != 0):
        k -= 1
    horizontalBounds[0] = k
    k = j
    while (object[midpoint][k] != 0 and k != width - 1):
        k += 1
    horizontalBounds[1] = k


cv2.namedWindow('main')
cv2.namedWindow('filtered')
cv2.setMouseCallback('main', onmouse)

def detect(object, size):
    height, width = object.shape
    objectFound, horizontalBounds, verticalBounds = scanPixelsForObject(object, height, width, size)
    return horizontalBounds, verticalBounds

while(True):

    hsv = capture(cv2.COLOR_BGR2HSV) #Võta kaamerast pilt
    if(hsv is None): #Kontroll, kas pilt on olemas
        print("Capture fucntion failed")
        break

    ballMask = cv2.inRange(hsv, ballLowerRange, ballUpperRange) #Filtreeri välja soovitava värviga objekt
    ballMask = blur(ballMask)
    horizontalBounds, verticalBounds = detect(ballMask, 1000)
    cv2.rectangle(hsv, (horizontalBounds[0], verticalBounds[1]), (horizontalBounds[1], verticalBounds[0],), (255,0,0),3)
    print("Object size: " + str((horizontalBounds[1]-horizontalBounds[0])*(verticalBounds[1] - verticalBounds[0])))

    # Display the resulting frame
    cv2.imshow('filtered', ballMask)
    cv2.imshow('main', hsv)
    if cv2.waitKey(1) & 0xFF == ord('q'): #Nupu 'q' vajutuse peale välju programmist
        break
    if cv2.waitKey(1) & 0xFF == ord('b'):
        ballLowerRange = np.array([255, 255, 255])
        ballUpperRange = np.array([0, 0, 0])

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()