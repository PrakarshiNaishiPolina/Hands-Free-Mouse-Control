import cv2 as cv
import mediapipe as mp
import pyautogui
import screen_brightness_control as sbc
import time
from pycaw.pycaw import AudioUtilities,IAudioEndpointVolume
from ctypes import cast,POINTER
from comtypes import CLSCTX_ALL

# Hands
mp_hands=mp.solutions.hands
hands=mp_hands.Hands(min_detection_confidence=0.7,min_tracking_confidence=0.7)
mp_draw=mp.solutions.drawing_utils

# Volume

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))


cap = cv.VideoCapture(0)
screen_width, screen_height = pyautogui.size()

screenshot_taken = False  # Flag to avoid multiple screenshots on one pinch

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv.flip(frame, 1)
    rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
            wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]

            x, y = int(index_tip.x * screen_width), int(index_tip.y * screen_height)
            pyautogui.moveTo(x, y)

            # Calculate distances for gestures
            pinch_distance = ((index_tip.x - thumb_tip.x)**2 + (index_tip.y - thumb_tip.y)**2) ** 0.5
            volume_distance = ((thumb_tip.x - pinky_tip.x)**2 + (thumb_tip.y - pinky_tip.y)**2) ** 0.5
            fist_distance = ((wrist.x - index_tip.x)**2 + (wrist.y - index_tip.y)**2) ** 0.5

            # Pinch gesture → Take screenshot
            if pinch_distance < 0.05:
                if not screenshot_taken:  
                    screenshot_taken = True
                    screenshot_name = f"screenshot_{int(time.time())}.png"
                    pyautogui.screenshot(screenshot_name)
                    print(f"Screenshot saved: {screenshot_name}")
            else:
                screenshot_taken = False  
            current_brightness = sbc.get_brightness()[0]
            if y < screen_height // 2:  # Hand up → Increase brightness
                sbc.set_brightness(min(current_brightness + 5, 100))
            else:                       # Hand down → Decrease brightness
                sbc.set_brightness(max(current_brightness - 5, 0))

            # Volume control with thumb + pinky gesture
            if volume_distance < 0.08:
                volume_level = volume.GetMasterVolumeLevelScalar()
                if y < screen_height // 2:    # Hand up → Increase volume
                    volume.SetMasterVolumeLevelScalar(min(volume_level + 0.1, 1.0), None)
                    print("Volume Increased")
                else:                         # Hand down → Decrease volume
                    volume.SetMasterVolumeLevelScalar(max(volume_level - 0.1, 0.0), None)
                    print("Volume Decreased")

            # Two-finger swipe gesture → Scroll
            if abs(index_tip.x - thumb_tip.x) > 0.2:  # Fingers far apart → scroll
                if index_tip.y < thumb_tip.y:
                    pyautogui.scroll(100)  # Scroll up
                else:
                    pyautogui.scroll(-100)  # Scroll down

            # Fist gesture → Lock the screen
            if fist_distance < 0.08:   # Fingers close to the wrist → Fist detected
                print("Locking Screen...")
                pyautogui.hotkey("win", "l")

    cv.imshow("Gesture Control", frame)

    if cv.waitKey(1) & 0xFF == 27:  # Press 'Esc' to exit
        break

cap.release()
cv.destroyAllWindows()