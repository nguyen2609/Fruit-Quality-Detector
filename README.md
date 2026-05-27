# Fruit Quality Detector with CounterFit, Laptop Camera, Azure Custom Vision, and LED

This project is a simple IoT-based fruit quality detection system. It uses a simulated distance sensor in CounterFit to trigger the laptop camera. When the fruit is within 30 cm, the camera captures an image and sends it to Azure Custom Vision for classification.

The system only responds to `ripe` and `unripe` results. If the AI model predicts `rotten`, the result is ignored completely.

---

## Project Flow

```text
CounterFit Distance Sensor
        ↓
If distance <= 300 mm
        ↓
Laptop Camera captures fruit image
        ↓
Image is sent to Azure Custom Vision
        ↓
Azure returns prediction result
        ↓
System checks the result
        ↓
ripe   → LED OFF
unripe → LED ON
rotten → ignored
```

---

## System Logic

| AI Result | Meaning | Terminal Output | LED Action |
|---|---|---|---|
| `ripe` | Fruit is ripe / acceptable | Show result and confidence | LED OFF |
| `unripe` | Fruit is unripe / not acceptable | Show result and confidence | LED ON |
| `rotten` | Fruit is rotten | Ignored completely | No action |
| Other result | Unknown class | Ignored | No action |

---

## Components Used

| Component | Type | Purpose |
|---|---|---|
| Laptop camera | Real hardware | Captures fruit images |
| CounterFit distance sensor | Simulated sensor | Triggers camera when fruit is within 30 cm |
| CounterFit LED actuator | Simulated actuator | Indicates unripe fruit |
| Azure Custom Vision | Cloud AI service | Classifies fruit image |

---

## Files in This Project

```text
fruit-quality-detector/
│
├── app.py
├── distance-sensor.py
├── captures/
└── README.md
```

### `app.py`

This is the main application file. It performs the complete project flow:

```text
Read distance from CounterFit
→ Trigger camera when distance <= 300 mm
→ Capture image from laptop camera
→ Save image to captures folder
→ Send image to Azure Custom Vision
→ Receive AI prediction
→ Control LED based on result
```

### `distance-sensor.py`

This file is used only for testing the CounterFit distance sensor. It reads the distance value from CounterFit and prints it in the terminal every 10 seconds.

Example output:

```text
Distance = 250 mm
Distance = 500 mm
Distance = 300 mm
```

This file is not required when running the main application, but it is useful for checking whether the simulated distance sensor is working correctly.

---

## Requirements

Install the required Python libraries:

```bash
pip install opencv-python requests counterfit counterfit-connection counterfit-shims-rpi-vl53l0x counterfit-shims-grove
```

If CounterFit has compatibility issues, install these versions:

```bash
pip install "flask==2.0.3" "werkzeug==2.0.3" "eventlet==0.33.3"
```

---

## CounterFit Setup

Start CounterFit:

```bash
counterfit
```

Then open the browser:

```text
http://127.0.0.1:5000/
```

The page should show:

```text
Connected
```

---

## Create the Distance Sensor

In the **Sensors** section, create:

```text
Sensor Type: Distance
Units: Millimeter
I²C address: 0x29
```

Click **Add**.

This sensor simulates the fruit distance from the camera.

Example values:

| Value | Distance | System Behavior |
|---:|---|---|
| `500` | 50 cm | Camera does not capture |
| `300` | 30 cm | Camera captures |
| `250` | 25 cm | Camera captures |
| `100` | 10 cm | Camera captures |

The camera is triggered when:

```text
distance <= 300 mm
```

---

## Create the LED Actuators

In the **Actuators** section, create:

```text
Actuator Type: LED
Pin: 0
```

This LED is used to indicate `unripe` fruit.

Create another LED if your current `app.py` still includes `led_rotten`:

```text
Actuator Type: LED
Pin: 1
```

However, in the final project logic, `rotten` is ignored completely.

---

## How to Run the Project

### Step 1: Start CounterFit

Open a terminal and run:

```bash
counterfit
```

Keep this terminal open.

### Step 2: Open the CounterFit Web Page

Open:

```text
http://127.0.0.1:5000/
```

Make sure the page shows:

```text
Connected
```

### Step 3: Run the Main App

Open another terminal and run:

```bash
python app.py
```

The laptop camera window will open.

### Step 4: Trigger the Camera

In CounterFit, set the distance value to:

```text
250
```

Then click **Set**.

Since `250 mm` is less than `300 mm`, the system will capture an image and send it to Azure Custom Vision.

---

## Expected Output

### If the AI result is `ripe`

```text
Distance = 250 mm
Fruit detected within 30 cm. Capturing image...
Image saved: captures/fruit_20260525_224932.jpg
AI Result: ripe
Confidence: 92.45%
Fruit is ripe. All LEDs OFF.
```

LED behavior:

```text
LED pin 0 OFF
```

---

### If the AI result is `unripe`

```text
Distance = 250 mm
Fruit detected within 30 cm. Capturing image...
Image saved: captures/fruit_20260525_224950.jpg
AI Result: unripe
Confidence: 88.10%
LED 0 ON: Fruit is unripe.
```

LED behavior:

```text
LED pin 0 ON
```

---

### If the AI result is `rotten`

The result is ignored completely.

The terminal will not show:

```text
AI Result: rotten
```

The LED will not change because of the rotten result.

---

## How to Stop the Program

Click on the camera window and press:

```text
Q
```

The program will stop, close the camera, and turn off the LED.

---

## Important Code Logic

The project uses this logic to ignore `rotten`:

```python
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
```

This means:

```text
rotten → do nothing
ripe → print result and turn LED off
unripe → print result and turn LED on
```

---

## Notes

- The distance sensor does not check fruit quality.
- The distance sensor only decides when the camera should capture an image.
- Fruit quality is determined by Azure Custom Vision based on the captured image.
- The laptop camera is used as the real image input.
- CounterFit is used to simulate the distance sensor and LED actuator.
- Captured images are saved in the `captures/` folder.
- The `rotten` class still exists in the AI model, but the program ignores it.

---

## Troubleshooting

### CounterFit shows `Disconnected`

Make sure the CounterFit server is running:

```bash
counterfit
```

Then refresh:

```text
http://127.0.0.1:5000/
```

---

### Port 5000 is already in use

If port 5000 is already being used, check the process:

```bash
netstat -ano | findstr :5000
```

Then stop the old process or close the old CounterFit terminal.

---

### Azure Proxy Error

If the terminal shows a proxy or SSL error, the network may be blocking the Azure request.

The code uses:

```python
session.trust_env = False
```

to prevent Python from using system proxy settings.

You can also try clearing proxy variables in PowerShell:

```powershell
Remove-Item Env:HTTP_PROXY -ErrorAction SilentlyContinue
Remove-Item Env:HTTPS_PROXY -ErrorAction SilentlyContinue
Remove-Item Env:http_proxy -ErrorAction SilentlyContinue
Remove-Item Env:https_proxy -ErrorAction SilentlyContinue
```

If it still does not work, try using a different network, such as a mobile hotspot.

---

### Camera cannot open

If the camera cannot open, change:

```python
camera = cv2.VideoCapture(0)
```

to:

```python
camera = cv2.VideoCapture(1)
```

Also close apps that may be using the camera, such as Zoom, Teams, or the Windows Camera app.

---

## Security Note

The Azure Prediction Key should not be shared publicly. If the key has been exposed, regenerate it in Azure Custom Vision and update the value in `app.py`.