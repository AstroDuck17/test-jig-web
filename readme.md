# FastAPI Test-Jig App

## Overview
This FastAPI application provides a simple web interface for testing hardware pin connections and running tests on various protocols (I2C, SPI, UART, PWM, ADC, GPIO). The API supports:
- Fetching pin connections via a GET endpoint.
- Running device-specific tests via a POST endpoint.

## Requirements
- Python 3.11
- FastAPI
- Uvicorn
- Board-specific libraries (e.g., Adafruit Blinka)
- Additional dependencies as required by your hardware modules

## Installation
1. Clone the repository:
   ```
   git clone <repository_url>
   ```
2. Navigate to the project directory:
   ```
   cd d:\college\SCRC\test-jig-main\test-jig-web
   ```
3. (Optional) Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```

## Running the Application
Start the FastAPI web server by running the `main.py` file:
```
python fastapi_app/main.py
```
This launches Uvicorn on [http://0.0.0.0:8000](http://0.0.0.0:8000).

Alternatively, you can start the server directly with Uvicorn:
```
uvicorn fastapi_app.main:app --host 0.0.0.0 --port 8000 --reload
```
### Development Setup
Project structure:
```
test-jig-web
├── webenv
└── test-jig-main
    └── fastapi_app
```
To run in development mode:
1. In the `test-jig-web` directory, activate the virtual environment:
   ```
   source webenv/bin/activate
   ```
2. Change directory into `test-jig-main`:
   ```
   cd test-jig-main
   ```
3. Start Uvicorn:
   ```
   uvicorn fastapi_app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   
## Using the App

### Home Page
- **GET /**  
  Opens the main interface with the associated HTML template (`index.html`).

### Getting Pin Connection Details
- **GET /pin-connection/{protocol}/{device}**  
  Replace `{protocol}` and `{device}` with values like `i2c` and `bh1750`.  
  **Example:**  
  `GET /pin-connection/i2c/bh1750`  
  Returns JSON with pin connection details for the device.

### Running a Test
- **POST /run-test/{protocol}/{device}**  
  Sends a request to run a specific test.  
  Replace `{protocol}` and `{device}` with the desired values.  
  **Example:**  
  `POST /run-test/spi/oled`  
  Captures and returns output (or error messages) from the test function.

## Logging and Debugging
- The test execution captures the standard output and returns it within the JSON response.
- Check the console where Uvicorn is running for additional logs or error messages.

## Customization
- Update the `PIN_MAPPING` dictionary in `routes.py` to add support for new protocols or devices.
- Edit the hardware-specific modules under the `lib` folder if modifications in device testing logic are needed.
- The FastAPI templates are located under `fastapi_app/templates` and static assets under `fastapi_app/static`.

## Further Information
For detailed workings of the hardware tests, examine the individual modules in `lib` (e.g., `lib/I2C/BH1750.py`, `lib/PWM/fade.py`).

---

*This README serves as a quick guide to set up and interact with the FastAPI Test-Jig application.*