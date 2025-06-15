import io, sys
import asyncio
import time
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from lib.pin_details import PIN_CONNECTION
from starlette.concurrency import run_in_threadpool

router = APIRouter()
templates = Jinja2Templates(directory="fastapi_app/templates")

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

TEST_STOP_FLAG = False

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

@router.get("/run-test/{protocol}/{device}")
async def run_test(protocol: str, device: str):
    global TEST_STOP_FLAG
    TEST_STOP_FLAG = False

    async def event_generator():
        protocol_lower = protocol.lower()
        device_lower = device.lower()
        scan_done = False  # new variable to ensure scan is performed only once
        while not TEST_STOP_FLAG:
            if protocol_lower == "i2c":
                if not scan_done:
                    try:
                        from smbus2 import SMBus
                        with SMBus(1) as bus:
                            addresses = []
                            for addr in range(0x03, 0x78):
                                try:
                                    bus.write_quick(addr)
                                    addresses.append(hex(addr))
                                except OSError:
                                    pass
                        yield f"data: I2C devices found: {addresses}\n\n"
                    except Exception as e:
                        yield f"data: Error scanning I2C bus: {e}\n\n"
                    scan_done = True
                if device_lower == "bh1750":
                    from lib.I2C.BH1750 import BH1750
                    result = await run_in_threadpool(BH1750().activate_gui)
                    yield f"data: {result if result is not None else 'No connections present'}\n\n"
                elif device_lower == "oled":
                    from lib.I2C.i2c_oled import I2C_OLED
                    result = await run_in_threadpool(I2C_OLED().activate_gui)
                    yield f"data: {result if result is not None else 'No connections present'}\n\n"
                elif device_lower == "mlx90614":
                    from lib.I2C.mlx90614 import MLX90614
                    result = await run_in_threadpool(MLX90614().activate_gui)
                    yield f"data: {result if result is not None else 'No connections present'}\n\n"
                else:
                    yield "data: Unknown I2C device\n\n"
            elif protocol_lower == "spi":
                if device_lower == "sd-card":
                    yield "data: (Test for SD Card Module not implemented)\n\n"
                elif device_lower == "oled":
                    from lib.SPI.spi_oled import SPI_OLED
                    result = await run_in_threadpool(lambda: SPI_OLED().activate_cli(image_path="c.bmp"))
                    yield f"data: {result if result is not None else 'No connections present'}\n\n"
                else:
                    yield "data: Unknown SPI device\n\n"
            elif protocol_lower == "uart":
                if device_lower == "pm sensor":
                    from lib.UART.PM_Sensor import SDS011
                    result = await run_in_threadpool(SDS011().activate_cli)
                    yield f"data: {result if result is not None else 'No connections present'}\n\n"
                else:
                    yield "data: Unknown UART device\n\n"
            elif protocol_lower == "pwm":
                if device_lower == "led-fading":
                    from lib.PWM.fade import LedFader
                    try:
                        result = await run_in_threadpool(lambda: LedFader(18).activate_cli())
                        yield f"data: {result if result is not None else 'No connections present'}\n\n"
                    except Exception as e:
                        yield f"data: LED fading test error: {e}\n\n"
                elif device_lower == "servo motor":
                    from lib.PWM.servo import ServoMotor
                    result = await run_in_threadpool(ServoMotor().activate_cli)
                    yield f"data: {result if result is not None else 'No connections present'}\n\n"
                elif device_lower == "rgb led":
                    from lib.PWM.rgb import RGBLED
                    try:
                        result = await asyncio.wait_for(run_in_threadpool(RGBLED().activate_cli), timeout=2.0)
                        yield f"data: {result if result is not None else 'No connections present'}\n\n"
                    except asyncio.TimeoutError:
                        yield "data: RGB LED test timed out (no connection?)\n\n"
                    except Exception as e:
                        yield f"data: RGB LED test error: {e}\n\n"
                else:
                    yield "data: Unknown PWM device\n\n"
            elif protocol_lower == "adc":
                yield "data: ADC test not implemented\n\n"
            elif protocol_lower == "gpio":
                if device_lower == "button":
                    from lib.GPIO.button import ButtonController
                    result = await run_in_threadpool(lambda: ButtonController(button_pin=5).activate_cli())
                    yield f"data: {result if result is not None else 'No connections present'}\n\n"
                else:
                    yield "data: Unknown GPIO device\n\n"
            else:
                yield f"data: Error: Pin mapping not defined for protocol '{protocol}' and device '{device}'.\n\n"
            await asyncio.sleep(1)
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.post("/stop-test")
async def stop_test():
    global TEST_STOP_FLAG
    TEST_STOP_FLAG = True
    return {"result": "Test stopped"}