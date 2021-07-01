import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math
import screen_brightness_control as sbc
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

wCam, hCam = 640, 480
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0

detector = htm.handDetector(detectionCon=0.5)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volBar = 400
volPer = 0
while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)
    if len(lmList) != 0:
        # print(lmList[4], lmList[8])

        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        x3, y3 = lmList[3][1], lmList[3][2]
        x4, y4 = lmList[12][1], lmList[12][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        cx1, cy1 = (x3 + x4) // 2, (y3 + y4) // 2

        cv2.circle(img, (x1, y1), 10, (50, 205, 115), cv2.FILLED)
        cv2.circle(img, (x2, y2), 10, (50, 205, 115), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (153, 50, 204), 3)
        cv2.circle(img, (cx, cy), 10, (50, 205, 115), cv2.FILLED)
        cv2.circle(img, (x3, y3), 10, (50, 205, 115), cv2.FILLED)
        cv2.circle(img, (x4, y4), 10, (50, 205, 115), cv2.FILLED)
        cv2.line(img, (x3, y3), (x4, y4), (153, 50, 204), 3)
        cv2.circle(img, (cx1, cy1), 10, (50, 205, 115), cv2.FILLED)

        length = math.hypot(x2 - x1, y2 - y1)
        length1=math.hypot(x4-x3, y4-y3)


        vol = np.interp(length, [20, 220], [minVol, maxVol])
        volPer = np.interp(length, [20, 220], [0, 100])
        # print(int(length), vol)
        volume.SetMasterVolumeLevel(vol, None)
        cv2.putText(img, f'Volume: {int(volPer)}%', (400, 50), cv2.FONT_HERSHEY_SCRIPT_COMPLEX,
                    1, (255, 0, 0), 3)


        if length1 in range(50, 70):
            sbc.set_brightness(30)
        elif length1 in range(70, 100):
            sbc.set_brightness(50)
        elif length1 in range(100, 150):
            sbc.set_brightness(85)
        elif length1 > 150:
            sbc.set_brightness(100)
        else:
            pass

    try:
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, f'FPS: {int(fps)}', (40, 50), cv2.FONT_ITALIC,
                    1, (239, 10, 228), 3)
    except ZeroDivisionError:
        print("You have got low frames")

    cv2.imshow("Gesture Volume Control", img)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("b"):
        break

cap.release()
cv2.destroyAllWindows()