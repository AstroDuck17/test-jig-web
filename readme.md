# SCRC TEST-JIG

A modular Python-based test-jig platform for Raspberry Pi 3 to test and interact with various hardware protocols and sensors/modules. Supports CLI, Tkinter GUI, and a FastAPI web application for running tests, viewing pin mappings, and logging results.

---

## Features

- **Protocols Supported:** I2C, SPI, UART, PWM, GPIO, ADC, RS485
- **Device Testing:** Sensors and modules like BH1750, OLED, MLX90614, SD Card, PM Sensor, LEDs, Servo, RGB, Potentiometer, TDS, LDR, DHT11, Ultrasonic, DS18B20, etc.
- **Interfaces:**
  - **Web App:** FastAPI web app (`uvicorn fastapi_app.main:app`)
  - **CLI:** Command-line interface (`main.py --cli`)
  - **GUI:** Tkinter graphical interface (`main.py --gui`)
- **Pin Mapping:** View pin connections for each device/protocol
- **Logging:** Download logs from web/GUI
- **RS485:** Advanced configuration and test page in web app

---

## Directory Structure

```
test-jig-web/
├── test-jig-web-update/
│   ├── cli.py
│   ├── gui.py
│   ├── main.py
│   ├── requirement.txt
│   ├── lib/
│   └── fastapi_app/
│       ├── main.py
│       ├── routes.py
│       ├── templates/
│       └── static/
├── README.md
├── requirements.txt
```

---

## Setup

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd test-jig-web
   ```

2. **Create and activate a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Enable required interfaces on Raspberry Pi**
   - Use `sudo raspi-config` to enable I2C, SPI, UART, etc.

---

## Usage of Web App

```bash
cd test-jig-web-update
uvicorn fastapi_app.main:app --host 0.0.0.0 --port 8000 --reload
```
- Open browser at `http://<raspberry-pi-ip>:8000`

---

## Supported Protocols & Devices

- **I2C:** BH1750, OLED, MLX90614
- **SPI:** SD Card Module, SPI OLED
- **UART:** PM Sensor
- **PWM:** LED (Fading), Servo Motor, RGB LED
- **ADC:** Potentiometer, TDS, LDR
- **GPIO:** LED, Button, Ultrasonic Sensor, DHT11, DS18B20
- **RS485:** Modbus communication (transmit/receive)

---

## Pin Mapping

Pin mapping for each device is available in the web interface and in `lib/pin_details.py`.

---
