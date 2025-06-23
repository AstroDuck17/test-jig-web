import io, sys
import asyncio
import time
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from lib.pin_details import PIN_CONNECTION
from starlette.concurrency import run_in_threadpool
import subprocess

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

# Replace the existing root endpoint with homepage view
@router.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    return templates.TemplateResponse("homepage.html", {"request": request})

# New endpoint for TestJig (current index.html)
@router.get("/testjig.html", response_class=HTMLResponse)
async def testjig_page(request: Request):
    return templates.TemplateResponse("testjig.html", {"request": request})

# New endpoint for TestJig (current index.html)
@router.get("/homepage.html", response_class=HTMLResponse)
async def testjig_page(request: Request):
    return templates.TemplateResponse("homepage.html", {"request": request})

# New endpoint for RS485 page
@router.get("/rs485.html", response_class=HTMLResponse)
async def rs485_page(request: Request):
    return templates.TemplateResponse("rs485.html", {"request": request})

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
                # New ADC branch: support Potentiometer, tds and ldr
                if device_lower == "pot":
                    from lib.ADC.pot import Pot
                    result = await run_in_threadpool(Pot().activate_gui)
                    yield f"data: {result}\n\n"
                elif device_lower == "tds":
                    from lib.ADC.tds import TDS_Sensor
                    result = await run_in_threadpool(lambda: TDS_Sensor(channel=0).activate_gui())
                    yield f"data: {result}\n\n"
                elif device_lower == "ldr":
                    from lib.ADC.ldr import LDRSensor
                    result = await run_in_threadpool(LDRSensor().activate_gui)
                    yield f"data: {result}\n\n"
                else:
                    yield "data: Unknown ADC device\n\n"
            elif protocol_lower == "gpio":
                # New GPIO branch: support LED, DHT11, ultrasonic sensor, DS18B20 (button already exists)
                if device_lower == "led":
                    from lib.GPIO.led import LEDController
                    result = await run_in_threadpool(lambda: LEDController(5).activate_cli())
                    yield f"data: {result}\n\n"
                elif device_lower == "button":
                    from lib.GPIO.button import ButtonController
                    result = await run_in_threadpool(lambda: ButtonController(6).activate_cli())
                    yield f"data: {result}\n\n"
                elif device_lower == "dht11":
                    import board
                    from lib.GPIO.dht import DHTSensor
                    result = await run_in_threadpool(lambda: DHTSensor(pin=board.D13).activate_cli())
                    yield f"data: {result}\n\n"
                elif device_lower == "ultrasonic sensor":
                    from lib.GPIO.ultrasonic import UltrasonicSensor
                    result = await run_in_threadpool(lambda: UltrasonicSensor(trigger_pin=26, echo_pin=19).activate_cli())
                    yield f"data: {result}\n\n"
                elif device_lower == "ds18b20":
                    from lib.GPIO.DS18B20 import DS18B20
                    result = await run_in_threadpool(DS18B20().activate_cli)
                    yield f"data: {result}\n\n"
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

# New global variable to hold RS485 process
RS485_PROCESS = None

@router.get("/run-rs485", response_class=StreamingResponse)
async def run_rs485(request: Request, mode: str, baudRate: int, parity: str, slaveId: int = 1, registerAddress: int = 0, countMode: int = 1, dataType: str = "uint"):
    global RS485_PROCESS
    args = []
    if mode.lower() == "receive":
        args = ["python", "lib/RS485/rsReceive.py", 
                "--baud_rate", str(baudRate),
                "--parity", parity,
                "--slave_id", str(slaveId),
                "--register_address", str(registerAddress)]
    elif mode.lower() == "transmit":
        args = ["python", "lib/RS485/rsTransmitter.py",
                "--baud_rate", str(baudRate),
                "--parity", parity,
                "--slave_id", str(slaveId),
                "--register_address", str(registerAddress),
                "--count_mode", str(countMode),
                "--data_type", dataType]
    else:
        return {"error": "Invalid mode."}

    RS485_PROCESS = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    
    async def event_generator():
        while True:
            line = RS485_PROCESS.stdout.readline()
            if line:
                yield f"data: {line}\n\n"
            elif RS485_PROCESS.poll() is not None:
                break
            await asyncio.sleep(0.1)
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.post("/stop-rs485")
async def stop_rs485():
    global RS485_PROCESS
    if RS485_PROCESS:
        RS485_PROCESS.terminate()
        RS485_PROCESS = None
    return {"result": "RS485 test stopped"}