from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from lib.pin_details import PIN_CONNECTION

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
    result = f"(Test output for {protocol} - {device} would appear here)"
    if protocol.lower() in PIN_MAPPING and device.lower() in PIN_MAPPING[protocol.lower()]:
        device_name = PIN_MAPPING[protocol.lower()][device.lower()]
        pin = PIN_CONNECTION(device_name)
        result = f"Pin Connections: {pin.pin_connections}\n" + result
    return {"result": result}