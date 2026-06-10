import cv2
import serial
import time

# ESP32 connection
try:
    esp = serial.Serial('COM5', 115200, timeout=1)
    time.sleep(2)
    print("ESP32 connected")
except:
    print("WARNING: ESP32 not connected")
    esp = None

# Eye detector
eye_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_eye.xml'
)

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("ERROR: Webcam not found!")
    exit()

closed_frames = 0
OPEN_THRESHOLD = 3

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (640, 480))
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    eyes = eye_cascade.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=6
    )

    # ---------------- OPEN EYES ----------------
    if len(eyes) > 0:
        closed_frames = 0

        cv2.putText(frame, "EYE OPEN", (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        if esp:
            esp.write(b'2')   # STOP buzzer + green LED

    # ---------------- CLOSED EYES ----------------
    else:
        closed_frames += 1

        cv2.putText(frame, "EYE CLOSED", (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        if closed_frames > OPEN_THRESHOLD:
            if esp:
                esp.write(b'1')   # buzzer ON + red LED

    cv2.imshow("Eye Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        if esp:
            esp.write(b'0')
        break

cap.release()
cv2.destroyAllWindows()

if esp:
    esp.close()
    