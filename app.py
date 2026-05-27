import cv2
import time
import os
import requests
from datetime import datetime

from counterfit_connection import CounterFitConnection
from counterfit_shims_rpi_vl53l0x.vl53l0x import VL53L0X
from counterfit_shims_grove.grove_led import GroveLed



# =========================
# CONFIG
# =========================

CounterFitConnection.init("127.0.0.1", 5000)

TRIGGER_DISTANCE_MM = 300
COOLDOWN_SECONDS = 5

PREDICTION_URL = 'https://fruit-quality-detector-prediction-33e8f.cognitiveservices.azure.com/customvision/v3.0/Prediction/48330246-0326-4c86-abee-a3391877e29e/classify/iterations/Iteration2/image'
PREDICTION_KEY = 'DuzwQCqVpO64ujy5COcN0vjfQVtKOxOFiyyLlM4imnsIASF4dUlyJQQJ99CEACqBBLyXJ3w3AAAIACOGnNST'

os.makedirs("captures", exist_ok=True)


# =========================
# SETUP COUNTERFIT SENSOR + LED
# =========================

distance_sensor = VL53L0X()
distance_sensor.begin()
led_unripe = GroveLed(0)
led_rotten = GroveLed(1)

led_unripe.off()
led_rotten.off()
# =========================
# AI CLASSIFICATION
# =========================

def classify_image(image_path):
    headers = {
        "Prediction-Key": PREDICTION_KEY,
        "Content-Type": "application/octet-stream"
    }

    session = requests.Session()
    session.trust_env = False  # Do not use system proxy settings

    with open(image_path, "rb") as image_file:
        response = session.post(
            PREDICTION_URL,
            headers=headers,
            data=image_file,
            timeout=30
        )

    if response.status_code != 200:
        print("Azure Custom Vision error:")
        print(response.status_code)
        print(response.text)
        return None, 0

    result = response.json()
    predictions = result["predictions"]

    best_prediction = max(predictions, key=lambda x: x["probability"])

    label = best_prediction["tagName"]
    confidence = best_prediction["probability"]

    return label, confidence


# =========================
# CAMERA SETUP
# =========================

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Cannot open laptop camera.")
    exit()

print("System started.")
print("Distance <= 300 mm will trigger the camera.")
print("Press Q to quit.")

last_capture_time = 0
last_distance = None
# =========================
# MAIN LOOP
# =========================

while True:
    ret, frame = camera.read()

    if not ret:
        print("Cannot read camera frame.")
        break

    cv2.imshow("Fruit Quality Camera", frame)

    try:
        distance_sensor.wait_ready()
        distance = distance_sensor.get_distance()
    except Exception as e:
        print("Cannot read distance from CounterFit.")
        print(e)
        time.sleep(5)
        continue
    if distance != last_distance:
        print(f"Distance = {distance} mm")
        last_distance = distance


    current_time = time.time()

    if distance <= TRIGGER_DISTANCE_MM and current_time - last_capture_time >= COOLDOWN_SECONDS:
        print("Fruit detected within 30 cm. Capturing image...")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_path = f"captures/fruit_{timestamp}.jpg"

        cv2.imwrite(image_path, frame)
        print(f"Image saved: {image_path}")

        try:
            label, confidence = classify_image(image_path)

            if label is not None:
                label = label.lower()

                if label == "rotten":
                    # Ignore rotten result completely
                    pass

                elif label == "ripe":
                    print(f"AI Result: {label}")
                    print(f"Confidence: {confidence * 100:.2f}%")
                    led_unripe.off()
                    led_rotten.off()
                    print("Fruit is ripe. All LEDs OFF.")

                elif label == "unripe":
                    print(f"AI Result: {label}")
                    print(f"Confidence: {confidence * 100:.2f}%")
                    led_unripe.on()
                    led_rotten.off()
                    print("LED 0 ON: Fruit is unripe.")

                else:
                    pass
                

        except Exception as e:
            print("Error while classifying image:")
            print(e)

        last_capture_time = current_time

    key = cv2.waitKey(1)

    if key == ord("q"):
        break


camera.release()
cv2.destroyAllWindows()
led_unripe.off()
led_rotten.off()
print("System stopped.")