import os
import cv2
from cvzone import HandTrackingModule as htm
import numpy as np

# Variables
width, heigth = 1280, 720
folderPath = './presentation'
imageNum = 0
hs, ws = int(120*1), int(213*1)
gestureThreshold = 300
buttonPressed = False
buttonCounter = 0
buttonDelay = 10
annotations = [[]]
annotationNumber = 0
annotationStart = False

# Camera Setup
cap = cv2.VideoCapture(0)
cap.set(3, width)
cap.set(4, heigth)

# Get List of presentation images
pathImages = sorted(os.listdir(folderPath), key=len)

# Hand Detector
detector = htm.HandDetector(detectionCon=0.8, maxHands=1)

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    fullPathImage = os.path.join(folderPath, pathImages[imageNum])
    currentSlide = cv2.imread(fullPathImage)
    w, h, _ = currentSlide.shape

    hands, img = detector.findHands(img)
    cv2.line(img, (0, gestureThreshold),
             (width, gestureThreshold), (0, 255, 0), 10)

    if hands and buttonPressed is False:
        hand = hands[0]
        fingers = detector.fingersUp(hand)
        cx, cy = hand['center']
        lmList = hand['lmList']

        # Constain values for easy drawing
        xVal = int(np.interp(lmList[8][0], (width/2, w), (0, width+640)))
        yVal = int(np.interp(lmList[8][1], (150, heigth-150), (0, h)))
        indexFinger = xVal, yVal
        if cy <= gestureThreshold:  # if hand is at the height of the face

            # Gesture 1 - Left Slide
            if fingers == [1, 0, 0, 0, 0]:
                annotationStart = False
                print('Left')
                if imageNum > 0:
                    buttonPressed = True
                    annotations = [[]]
                    annotationNumber = 0
                    annotationStart = False
                    imageNum -= 1

            # Gesture 2 - Right Slide
            if fingers == [0, 0, 0, 0, 1]:
                annotationStart = False
                print('Right')
                if imageNum < len(pathImages)-1:
                    buttonPressed = True
                    annotations = [[]]
                    annotationNumber = 0
                    annotationStart = False
                    imageNum += 1

        # Gesture 3 - Show Pointer
        if fingers == [0, 1, 1, 0, 0]:
            annotationStart = False
            cv2.circle(currentSlide, indexFinger, 12, (0, 0, 255), cv2.FILLED)

        # Gesture 4 - Draw
        if fingers == [0, 1, 0, 0, 0]:
            if annotationStart is False:
                annotationStart = True
                annotationNumber += 1
                annotations.append([])
            cv2.circle(currentSlide, indexFinger, 12, (0, 0, 255), cv2.FILLED)
            annotations[annotationNumber].append(indexFinger)
        else:
            annotationStart = False

        if fingers == [0, 1, 1, 1, 0]:
            if annotations:
                if annotationNumber > -1:
                    annotations.pop(-1)
                    annotationNumber -= 1
                    buttonPressed = True
    else:
        annotationStart = False

    if buttonPressed:
        buttonCounter += 1
        if buttonCounter > buttonDelay:
            buttonCounter = 0
            buttonPressed = False

    for i in range(len(annotations)):
        for j in range(len(annotations[i])):
            if j != 0:
                cv2.line(currentSlide, annotations[i][j-1],
                         annotations[i][j], (0, 0, 255), 12)

    # Adding Small Image
    cv2.namedWindow('Slides', cv2.WINDOW_KEEPRATIO)
    imgSmall = cv2.resize(img, (ws, hs))
    currentSlide[0:hs, 0:ws] = imgSmall

    # cv2.imshow('Image', img)
    cv2.imshow('Slides', currentSlide)
    key = cv2.waitKey(1)
    if key == ord('q'):
        break
