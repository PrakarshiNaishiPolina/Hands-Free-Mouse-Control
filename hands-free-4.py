import cv2 as cv
import screen_brightness_control as sbc
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
from pynput import keyboard

# Initialize audio interface
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)

# to set volume
def set_volume(vol):
    vol = max(0.0, min(vol, 1.0))  
    volume.SetMasterVolumeLevelScalar(vol, None)
def on_press(key):
    try:
        if key.char == '+':  # Increase volume
            current_vol = volume.GetMasterVolumeLevelScalar()
            set_volume(current_vol + 0.05)
        elif key.char == '-':  # Decrease volume
            current_vol = volume.GetMasterVolumeLevelScalar()
            set_volume(current_vol - 0.05)
    except AttributeError:
        pass

# Display camera feed
cap = cv.VideoCapture(0)

print("Press '+' to increase volume, '-' to decrease.")
with keyboard.Listener(on_press=on_press) as listener:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Get current brightness
        brightness = sbc.get_brightness(display=0)[0] / 100

        # Map brightness to volume
        set_volume(brightness)

        # Display feed with brightness and volume info
        cv.putText(frame, f'Brightness: {int(brightness*100)}%', (10, 30), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv.putText(frame, f'Volume: {int(brightness*100)}%', (10, 60), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv.imshow('Camera Feed', frame)

        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv.destroyAllWindows()