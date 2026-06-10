import cv2
import serial
import winsound
import threading

# ESP32 (change COM port if needed)
try:
    esp = serial.Serial('COM5', 115200, timeout=1)
except:
    print("WARNING: ESP32 not connected")
    esp = None

# Eye detector
eye_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_eye.xml'
)

# Webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("ERROR: Webcam not found!")
    exit()

state = ""

def play_alarm():
    # Non-blocking beep (won't freeze camera)
    winsound.Beep(1500, 1000)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    eyes = eye_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5
    )

    # ---------------- OPEN EYES ----------------
    if len(eyes) > 0:

        cv2.putText(frame, "EYE OPEN", (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        for (x, y, w, h) in eyes:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        if state != "OPEN":
            state = "OPEN"
            print("EYES OPEN")

            if esp:
                esp.write(b'2')

    # ---------------- CLOSED EYES ----------------
    else:

        cv2.putText(frame, "EYE CLOSED", (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        if state != "CLOSED":
            state = "CLOSED"
            print("ALARM TRIGGERED")

            if esp:
                esp.write(b'1')

            # IMPORTANT: run sound in background (no freeze)
            threading.Thread(target=play_alarm, daemon=True).start()

    cv2.imshow("Eye Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        if esp:
            esp.write(b'0')
        break

cap.release()
cv2.destroyAllWindows()
if esp:
    esp.close()