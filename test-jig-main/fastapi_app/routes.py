from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from lib.pin_details import PIN_CONNECTION
import io, sys
from starlette.concurrency import run_in_threadpool
import asyncio

router = APIRouter()
templates = Jinja2Templates(directory="fastapi_app/templates")

# Mapping of protocol and device values to the string to pass to PIN_CONNECTION.
PIN_MAPPING = {
    "i2c": {
        "bh1750": "BH1750",
        "oled": "OLED",
        "mlx90614": "MXL90614"
    },
    "spi": {
        "sd-card": "SD Card MOdule",
        "oled": "SPI OLED"
    },
    "uart": {
        "pm sensor": "PM Sensor"
    },
    "pwm": {
        "led-fading": "LED_FADE",
        "servo motor": "Servo Motor",
        "rgb led": "RGB LED"
    },
    "adc": {
        "pot": "Potentiometer",
        "tds": "tds",
        "ldr": "ldr"
    },
    "gpio": {
        "led": "LED",
        "button": "BUTTON",
        "ultrasonic sensor": "ultrasonic sensor",
        "dht11": "DHT11",
        "ds18b20": "DS18B20"
    }
}

@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/pin-connection/{protocol}/{device}")
async def get_pin_connection(protocol: str, device: str):
    protocol_key = protocol.lower()
    device_key = device.lower()
    if protocol_key in PIN_MAPPING and device_key in PIN_MAPPING[protocol_key]:
        device_name = PIN_MAPPING[protocol_key][device_key]
        pin = PIN_CONNECTION(device_name)
        return {"protocol": protocol, "device": device, "pin_connections": pin.pin_connections}
    else:
        return {"error": f"Pin connection not defined for protocol '{protocol}' and device '{device}'."}

@router.post("/run-test/{protocol}/{device}")
async def run_test(protocol: str, device: str):
    print(f"Received run_test POST: protocol='{protocol}', device='{device}'")
    old_stdout = sys.stdout
    sys.stdout = mystdout = io.StringIO()
    protocol_lower = protocol.lower()
    device_lower = device.lower()

    # Pre-check: verify that the proper connection exists.
    if protocol_lower in PIN_MAPPING and device_lower in PIN_MAPPING[protocol_lower]:
        device_name = PIN_MAPPING[protocol_lower][device_lower]
        pin = PIN_CONNECTION(device_name)
        if not pin.pin_connections:  # Adjust check as needed for your valid connection condition.
            print(f"Error: Connection to '{device_name}' not available.")
            sys.stdout = old_stdout
            return {"result": f"Error: Connection to '{device_name}' not available."}
    else:
        print(f"Error: Pin mapping not defined for protocol '{protocol}' and device '{device}'.")
        sys.stdout = old_stdout
        return {"result": f"Error: Pin mapping not defined for protocol '{protocol}' and device '{device}'."}

    try:
        if protocol_lower == "i2c":
            if device_lower == "bh1750":
                from lib.I2C.BH1750 import BH1750
                try:
                    await asyncio.wait_for(run_in_threadpool(BH1750().activate_gui), timeout=2.0)
                except asyncio.TimeoutError:
                    print("")  # Print empty output if timed out
            elif device_lower == "oled":
                from lib.I2C.i2c_oled import I2C_OLED
                await run_in_threadpool(I2C_OLED().activate_gui)
            elif device_lower == "mlx90614":
                from lib.I2C.mlx90614 import MLX90614
                await run_in_threadpool(MLX90614().activate_gui)
            else:
                print("Unknown I2C device")
        elif protocol_lower == "spi":
            if device_lower == "sd-card":
                print("(Test for SD Card Module not implemented)")
            elif device_lower == "oled":
                from lib.SPI.spi_oled import SPI_OLED
                await run_in_threadpool(lambda: SPI_OLED().activate_cli(image_path="c.bmp"))
            else:
                print("Unknown SPI device")
        elif protocol_lower == "uart":
            if device_lower == "pm sensor":
                from lib.UART.PM_Sensor import SDS011
                await run_in_threadpool(SDS011().activate_cli)
            else:
                print("Unknown UART device")
        elif protocol_lower == "pwm":
            if device_lower == "led-fading":
                from lib.PWM.fade import LedFader
                try:
                    await run_in_threadpool(LedFader(18).activate_cli)
                except Exception as e:
                    print(f"LED fading test error: {e}")
            elif device_lower == "servo motor":
                from lib.PWM.servo import ServoMotor
                await run_in_threadpool(ServoMotor().activate_cli)
            elif device_lower == "rgb led":
                from lib.PWM.rgb import RGBLED
                try:
                    await asyncio.wait_for(run_in_threadpool(RGBLED().activate_cli), timeout=2.0)
                except asyncio.TimeoutError:
                    print("RGB LED test timed out (no connection?)")
                except Exception as e:
                    print(f"RGB LED test error: {e}")
            else:
                print("Unknown PWM device")
        elif protocol_lower == "adc":
            print("ADC test not implemented")
        elif protocol_lower == "gpio":
            if device_lower == "button":
                from lib.GPIO.button import ButtonController
                await run_in_threadpool(lambda: ButtonController(button_pin=5).activate_cli())
            else:
                print("Unknown GPIO device")
    except asyncio.CancelledError:
        print("Test was cancelled due to shutdown.")
        return {"result": "Test cancelled"}
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        sys.stdout = old_stdout
    result = mystdout.getvalue()
    if not result.strip():
        result = "No input"
    return {"result": result}