import cv2
import pyautogui
import time
from pynput import keyboard
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL

# Initialize variables
motion_detected = False
last_motion_time = time.time()

# Pycaw setup for volume control
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)

# Function to control volume
def set_volume(vol):
    vol = max(0.0, min(vol, 1.0))
    volume.SetMasterVolumeLevelScalar(vol, None)

# Motion detection with OpenCV
cap = cv2.VideoCapture(0)
ret, frame1 = cap.read()
ret, frame2 = cap.read()

def on_press(key):
    global last_motion_time
    last_motion_time = time.time()  # Reset motion time on keypress

# Listen for keyboard activity
listener = keyboard.Listener(on_press=on_press)
listener.start()

print("Press 'q' to exit.")
while cap.isOpened():
    # Motion detection
    diff = cv2.absdiff(frame1, frame2)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
    dilated = cv2.dilate(thresh, None, iterations=3)
    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) > 0:
        motion_detected = True
        last_motion_time = time.time()
    else:
        motion_detected = False

    # Display motion contours
    for contour in contours:
        if cv2.contourArea(contour) < 5000:
            continue
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(frame1, (x, y), (x + w, y + h), (0, 255, 0), 2)

    cv2.imshow('Motion Detector', frame1)
    frame1 = frame2
    ret, frame2 = cap.read()

    # Check for inactivity
    idle_time = time.time() - last_motion_time

    if idle_time > 10:  # 10 seconds of inactivity
        print("No motion detected. Locking screen...")
        pyautogui.hotkey('win', 'l')  # Lock the screen
        set_volume(0.1)  # Reduce volume to 10%

    # Quit condition
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
listener.stop()
