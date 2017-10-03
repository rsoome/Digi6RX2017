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
        return None, None

    img = cv2.cvtColor(frame, colorScheme) #Pane pilt etteantud värviskeemi
    return frame, img

def blur(img):
    kernel = np.ones((30,30), np.uint8)  #//TODO: Find values to put in the kernel
    dilation = cv2.dilate(img, kernel, 1) #Udusta pilti //TODO: püüda dilationist ja erotionist paremini aru saada
    kernel = np.ones((10,10), np.uint8)   #//TODO: Find values to put in the kernel
    erotion = cv2.erode(dilation, kernel, 1) #Teravda pilti
    return erotion

# --------------------------------------- verdicalLowerBound=vLB
# |           |             |           |
# |     8     |      7      |      9    |
# |           |             |           |
# |-----------|-------------|-----------| vLB+(vUB-vLB)/3
# |           |             |           |
# |     5     |      4      |      6    |
# |           |             |           |
# |-----------|-------------|-----------| vLB+2*((vUB-vLB)/3)
# |           |             |           |
# |     2     |      1      |      3    |
# |           |             |           |
# --------------------------------------- verticalUpperBound=vUB
# ^hLB+(hUB-hLB)/3   hLB+2*((hUB-hLB)/3)^
# ^                                     ^
# horizontalLowerBound=hLB      horizontalUpperBound=hUB
def findObject(mainImg, img, verticalLowerBound, verticalUpperBound, horizontalLowerBound, horizontalUpperBound, minObjectSize, minImgArea):
    horizontalBounds = np.array([horizontalUpperBound, 0])
    verticalBounds = np.array([verticalUpperBound, 0])
    objectFound = False

    verticalThird = (verticalLowerBound + (verticalUpperBound - verticalLowerBound) // 3)
    verticalTwoThirds = (verticalLowerBound + 2 * (verticalUpperBound - verticalLowerBound) // 3)
    horizontalThird = (horizontalLowerBound + (horizontalUpperBound - horizontalLowerBound) // 3)
    horizontalTwoThirds = (horizontalLowerBound + 2 * (horizontalUpperBound - horizontalLowerBound) // 3)


    verticalLowerBounds = [verticalTwoThirds,verticalTwoThirds, verticalTwoThirds,
                          verticalThird, verticalThird, verticalThird,
                           verticalLowerBound, verticalLowerBound, verticalLowerBound]

    verticalUpperBounds = [verticalUpperBound, verticalUpperBound, verticalUpperBound,
                           verticalTwoThirds, verticalTwoThirds, verticalTwoThirds,
                           verticalThird, verticalThird, verticalThird]

    horizontalLowerBounds = [horizontalThird, horizontalLowerBound, horizontalTwoThirds,
                             horizontalThird, horizontalLowerBound, horizontalTwoThirds,
                             horizontalThird, horizontalLowerBound, horizontalTwoThirds]

    horizontalUpperBounds = [horizontalTwoThirds, horizontalThird, horizontalUpperBound,
                             horizontalTwoThirds, horizontalThird, horizontalUpperBound,
                             horizontalTwoThirds, horizontalThird, horizontalUpperBound]

    if((verticalUpperBound - verticalLowerBound)*(horizontalUpperBound - horizontalLowerBound) > minImgArea):
        #print("minImgArea: " + str(minImgArea) + " img area: " + str((verticalUpperBound - verticalLowerBound)*(horizontalUpperBound - horizontalLowerBound)))
        for i in range(len(verticalLowerBounds)):
#            cv2.rectangle(mainImg, (horizontalLowerBounds[i], verticalUpperBounds[i]), (horizontalUpperBounds[i], verticalLowerBounds[i]),
#                          (0, 0, 255), 1)
            objectFound, horizontalBounds, verticalBounds = findObject(mainImg, img, verticalLowerBounds[i], verticalUpperBounds[i],
                                                                       horizontalLowerBounds[i], horizontalUpperBounds[i],
                                                                       minObjectSize*3, minImgArea)
            if(objectFound):
                return objectFound, horizontalBounds, verticalBounds
    else:
        objectFound, horizontalBounds, verticalBounds = scanPixelsForObject(img, verticalLowerBound, verticalUpperBound, horizontalLowerBound,
                                horizontalUpperBound, minObjectSize, horizontalBounds, verticalBounds)
    return objectFound, horizontalBounds, verticalBounds



#Scans through pixels to find an object with area at least as big as given minSize
#img - the image to scan
#height - the upper bound to which the image is scanned vertically
#width - the upper bound to which the image is scanned horizontally
#minSize - the minimum size of the object
#returns whether the object was found, its horizontal and vertical bounds
def scanPixelsForObject(img, verticalLowerBound, verticalUpperBound, horizontalLowerBound, horizontalUpperBound,
                        minSize, horizontalBounds, verticalBounds):
    #scan through the pixels
    for i in range(verticalLowerBound, verticalUpperBound):
        for j in range(horizontalLowerBound, horizontalUpperBound):
            #If a non black pixel is found, it is the bottom most pixel of the objects location.
            #Also check whether the pixel is already in the range of the previously found object,
            #if it's a pixel in the already found object, scan next pixel.
            if(img[i][j]!= 0 and (i < verticalBounds[0] or i > verticalBounds[1])
               and (j < horizontalBounds[0] or j > horizontalBounds[1])):
                findBounds(img, verticalUpperBound, horizontalUpperBound, horizontalBounds, verticalBounds, i, j)
                objectWidth = (horizontalBounds[1] - horizontalBounds[0])
                objectHeight = (verticalBounds[1] - verticalBounds[0])
                #Check whether the object's size is at least minSize
                if(objectWidth * objectHeight >= minSize):
                    #Object found
                    return True, horizontalBounds, verticalBounds

    #Object not found
    return False, horizontalBounds, verticalBounds

#Finds the boundary coordinates of an object starting from a given pixel coordinates
#img - the image from which to look for the coordinates
#horizontalBounds - the array where horizontal coordinates are saved
#verticalBounds - the array where vertical coordinates are saved
#verticalCoordinate - the starting vertical coordinate
#horizontalCoordinate - the starting horizontal coordinate
def findBounds(img, height, width, horizontalBounds, verticalBounds, verticalCoordinate, horizontalCoordinate):
    #The given vertical coordinate is expected to be the bottom most coordinate of the object
    k = verticalCoordinate
    while (img[k][horizontalCoordinate] != 0 and k != 0):
        k -= 1
    verticalBounds[0] = k
    k = verticalCoordinate
    #Iterate through coordinates starting from the bottom coordinate until a black pixel is found
    #or the edge of the image is reached.
    for k in range(verticalCoordinate, height):
        #Black pixel found or image edge reached, this is the upper vertical coordinate of the object
        if img[k][horizontalCoordinate] == 0 or k == height - 1:
            verticalBounds[1] = k
            break

    #The object is expected to be symmetrical from vertical axis so the height of the object
    #is divided by 2 to find the midpoint. From the midpoint pixels are scanned from both sides of the point
    #if a black pixel or image edge is reached.
    midpoint = verticalBounds[0] + (verticalBounds[1] - verticalBounds[0]) // 2
    k = horizontalCoordinate
    while (img[midpoint][k] != 0 and k != 0):
        k -= 1
    horizontalBounds[0] = k
    k = horizontalCoordinate
    while (img[midpoint][k] != 0 and k != width - 1):
        k += 1
    horizontalBounds[1] = k


cv2.namedWindow('main')
cv2.namedWindow('filtered')
cv2.setMouseCallback('main', onmouse)

def detect(mainImg, object, size):
    height, width = object.shape
    #objectFound, horizontalBounds, verticalBounds = scanPixelsForObject(object, 0, height, 0, width, size, np.array([width, 0]), verticalBounds = np.array([height, 0]))
    objectFound, horizontalBounds, verticalBounds = \
        findObject(mainImg, object, 0, height, 0, width,
                 100, 30000)
    return horizontalBounds, verticalBounds

while(True):

    frame, hsv = capture(cv2.COLOR_BGR2HSV) #Võta kaamerast pilt
    if(frame is None): #Kontroll, kas pilt on olemas
        print("Capture fucntion failed")
        break

    ballMask = cv2.inRange(hsv, ballLowerRange, ballUpperRange) #Filtreeri välja soovitava värviga objekt
    ballMask = blur(ballMask)
    horizontalBounds, verticalBounds = detect(frame, ballMask, 1000)
    cv2.rectangle(frame, (horizontalBounds[0], verticalBounds[1]), (horizontalBounds[1], verticalBounds[0],), (255,0,0),3)
    print("Object size: " + str((horizontalBounds[1]-horizontalBounds[0])*(verticalBounds[1] - verticalBounds[0])))

    # Display the resulting frame
    cv2.imshow('filtered', ballMask)
    cv2.imshow('main', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): #Nupu 'q' vajutuse peale välju programmist
        break
    if cv2.waitKey(1) & 0xFF == ord('b'):
        ballLowerRange = np.array([255, 255, 255])
        ballUpperRange = np.array([0, 0, 0])

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()