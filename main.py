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

    blr = blur(frame) #Pilt udusemaks
    img = cv2.cvtColor(blr, colorScheme) #Pane pilt etteantud värviskeemi
    return img

def blur(img):
    kernel = np.ones((25,25), np.uint8)  #//TODO: Find values to put in the kernel
    dilation = cv2.dilate(img, kernel, 1) #Udusta pilti //TODO: püüda dilationist ja erotionist paremini aru saada
    kernel = np.ones((8,8), np.uint8)   #//TODO: Find values to put in the kernel
    erotion = cv2.erode(dilation, kernel, 1) #Teravda pilti
    return erotion

cv2.namedWindow('main')
cv2.namedWindow('filtered')
cv2.setMouseCallback('main', onmouse)

while(True):

    hsv = capture(cv2.COLOR_BGR2HSV) #Võta kaamerast pilt
    if(hsv is None): #Kontroll, kas pilt on olemas
        print("Capture fucntion failed")
        break

    ballMask = cv2.inRange(hsv, ballLowerRange, ballUpperRange) #Filtreeri välja soovitava värviga objekt

    # Display the resulting frame
    cv2.imshow('filtered', ballMask)
    cv2.imshow('main', hsv)
    if cv2.waitKey(1) & 0xFF == ord('q'): #Nupu 'q' vajutuse peale välju programmist
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()