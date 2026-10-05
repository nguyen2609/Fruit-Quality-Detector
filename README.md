# Fruit Quality Detector

This project is an IoT prototype that uses a simulated distance sensor in CounterFit to trigger a laptop camera, capture a fruit image, and send it to Azure Custom Vision for classification.

The system currently recognizes two classes:

- `ripe` → LED turned OFF
- `unripe` → LED turned ON
- `rotten` → ignored

---

## Project Overview

```text
CounterFit distance sensor
        ↓
Distance <= 300 mm?
        ↓
Capture image with laptop camera
        ↓
Send image to Azure Custom Vision
        ↓
Check prediction result
        ↓
ripe   -> LED OFF
unripe -> LED ON
rotten -> ignore
```

---

## Components

| Component | Type | Purpose |
|---|---|---|
| Laptop camera | Real hardware | Captures the fruit image |
| CounterFit Distance Sensor | Simulated sensor | Detects when the fruit is close enough |
| CounterFit LED actuator | Simulated actuator | Shows `unripe` status |
| Azure Custom Vision | Cloud AI service | Classifies the image |

---

## Files in This Project

```text
IOT/
├── app.py
├── distance-sensor.py
├── requirements.txt
├── README.md
└── captures/   (created automatically when app runs)
```

### `app.py`
Main program. It:

1. Connects to CounterFit
2. Reads distance from the sensor
3. Triggers the camera when distance is `<= 300 mm`
4. Saves the captured image to `captures/`
5. Sends the image to Azure Custom Vision
6. Processes the result and controls the LED

### `distance-sensor.py`
Used only to test the simulated sensor. It reads the current distance from CounterFit and prints it every 10 seconds.

### `requirements.txt`
Contains the Python packages needed to run the project.

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

If needed, use the compatibility fix:

```bash
pip install "flask==2.0.3" "werkzeug==2.0.3" "eventlet==0.33.3"
```

---

## Start CounterFit

Run:

```bash
counterfit
```

Then open:

```text
http://127.0.0.1:5000/
```

Make sure the page shows `Connected`.

---

## Create the virtual sensor and LED

In CounterFit:

### Distance sensor
- Sensor Type: `Distance`
- Units: `Millimeter`
- I²C address: `0x29`

### LED actuator
- Actuator Type: `LED`
- Pin: `0`

The code in `app.py` uses:

```python
led_unripe = GroveLed(0)
led_rotten = GroveLed(1)
```

So the hardware setup should match that logic. `led_rotten` is created but not used for output when the label is `rotten`.

---

## Run the project

### Step 1
Open a terminal and start CounterFit:

```bash
counterfit
```

### Step 2
Open another terminal and run the app:

```bash
python app.py
```

### Step 3
Set the CounterFit distance sensor to a value such as:

```text
250
```

Since `250 <= 300`, the system will capture an image and classify it.

---

## Example behavior

When the image is classified as `ripe`:

```text
Distance = 250 mm
Fruit detected within 30 cm. Capturing image...
Image saved: captures/fruit_20260525_224932.jpg
AI Result: ripe
Confidence: 92.45%
Fruit is ripe. All LEDs OFF.
```

When the image is classified as `unripe`:

```text
Distance = 250 mm
Fruit detected within 30 cm. Capturing image...
Image saved: captures/fruit_20260525_224950.jpg
AI Result: unripe
Confidence: 88.10%
LED 0 ON: Fruit is unripe.
```

When the image is classified as `rotten`:

```text
The result is ignored.
```

---

## Important logic

The core logic in `app.py` is:

```python
if label is not None:
    label = label.lower()

    if label == "rotten":
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
```

This means:

- `rotten` → ignored
- `ripe` → print result and turn LED OFF
- `unripe` → print result and turn LED ON

---

## Stop the app

Click the camera window and press:

```text
Q
```

The program will close the camera and turn off the LED.

---

## Troubleshooting

### CounterFit shows `Disconnected`

Start CounterFit again:

```bash
counterfit
```

Then refresh:

```text
http://127.0.0.1:5000/
```

### Port 5000 is in use

```bash
netstat -ano | findstr :5000
```

Then stop the process using the port.

### Azure proxy or SSL error

The code sets:

```python
session.trust_env = False
```

This prevents Python from using system proxy settings. If needed, clear them in PowerShell:

```powershell
Remove-Item Env:HTTP_PROXY -ErrorAction SilentlyContinue
Remove-Item Env:HTTPS_PROXY -ErrorAction SilentlyContinue
Remove-Item Env:http_proxy -ErrorAction SilentlyContinue
Remove-Item Env:https_proxy -ErrorAction SilentlyContinue
```

### Camera cannot open

If `cv2.VideoCapture(0)` fails, try:

```python
camera = cv2.VideoCapture(1)
```

Also close other apps using the webcam such as Zoom, Teams, or the Windows Camera app.

---

## Security note

Do not publish the Azure Prediction Key in public repositories. In a real project, store it in environment variables or a secure config file instead of hardcoding it directly in `app.py`.
