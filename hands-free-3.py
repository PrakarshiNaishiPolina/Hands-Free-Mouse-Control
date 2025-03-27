import cv2 as cv
import mediapipe as mp

mp_hands=mp.solutions.hands  # load the hand tracking module
mp_drawing=mp.solutions.drawing_utils # load the drawing utility for drawing hand landmarks

hands=mp_hands.Hands(min_detection_confidence=0.5,min_tracking_confidence=0.3)

cap=cv.VideoCapture(0)

while cap.isOpened():
    ret,frame=cap.read()
    if not ret:
        break

    frame_rgb=cv.cvtColor(frame,cv.COLOR_BGR2RGB)

    results=hands.process(frame_rgb)
    if results.multi_hand_landmarks: # contains the landmark coordinates of the detected hands
        for hand_landmarks in results.multi_hand_landmarks:
            index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

            h,w,_=frame.shape
            x,y= int(index_finger_tip.x * w), int(index_finger_tip.y * h)
            cv.circle(frame, (x, y), 10, (0, 255, 0), -1)

            # Draw landmarks on the hand
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS) 

            # draws the hand landmarks and the connections between them.

    # Show the output
    cv.imshow("Hand Tracking", frame)

    if cv.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv.destroyAllWindows()
