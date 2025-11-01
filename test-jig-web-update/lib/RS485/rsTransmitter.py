#!/usr/bin/env python3
import sys
import time
import argparse
import logging
from pymodbus.server.sync import StartSerialServer
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext, ModbusSparseDataBlock
from pymodbus.transaction import ModbusRtuFramer
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.constants import Endian

# Configure logging to show only errors
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.ERROR)

def parse_args():
    parser = argparse.ArgumentParser(description="RS485 Transmit Test")
    parser.add_argument("--baud_rate", type=int, default=9600, help="Baud rate")
    parser.add_argument("--parity", type=str, default="E", help="Parity bit")
    parser.add_argument("--slave_id", type=int, default=1, help="Slave ID")
    parser.add_argument("--register_address", type=int, required=True, help="Register Address")
    parser.add_argument("--count_mode", type=int, choices=[1,2], required=True, help="Count Mode: 1 for Single, 2 for Double")
    parser.add_argument("--data_type", type=str, choices=["float", "long", "uint"], required=True, help="Data Type")
    # New arguments for stopbits and bytesize
    parser.add_argument("--stopbits", type=int, choices=[1,2], default=1, help="Stopbits, 1 or 2")
    parser.add_argument("--bytesize", type=int, choices=[7,8], default=8, help="Bytesize, 7 or 8")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout in seconds")
    parser.add_argument("--register_value", type=float, required=True, help="Register value")
    return parser.parse_args()


# Basic configuration for Modbus server

def configure_modbus():
    # Baud Rate selection
    baud_rate_choices = {1: 9600, 2: 115200}
    baud_choice = int(input('''Baud Rate:
    1. 9600
    2. 115200
Choose Baud Rate: ''').strip())
    baud_rate = baud_rate_choices.get(baud_choice, 9600)

    # Parity selection
    parity_choices = {1: 'E', 2: 'N', 3: 'O'}
    parity_choice = int(input('''Parity Bit:
    1. E (Even)
    2. N (None)
    3. O (Odd)
Choose Parity Bit: ''').strip())
    parity = parity_choices.get(parity_choice, 'E')

    # Slave ID selection
    slave_id = int(input("Enter the Slave ID: ").strip())

    print("✅ Configuration complete. Starting server...")
    return baud_rate, parity, slave_id


def build_registers(count_mode, data_type, register_address, value):
    builder = BinaryPayloadBuilder(byteorder=Endian.Big, wordorder=Endian.Little)
    
    if count_mode == 1 and data_type == 'uint':
        builder.add_16bit_uint(int(value))
    elif count_mode == 2:
        if data_type == 'float':
            builder.add_32bit_float(value)
        elif data_type == 'long':
            builder.add_32bit_int(int(value))
        else:
            print("❌ Unsupported combination of count mode and data type.")
            sys.exit(1)
    else:
        print("❌ Unsupported combination of count mode and data type.")
        sys.exit(1)
    return builder.to_registers()


def start_modbus_server_with_timeout(context, baud_rate, parity, stopbits, bytesize, timeout_seconds):
    """Start Modbus server with timeout"""
    import threading
    
    def run_server():
        StartSerialServer(
            context,
            framer=ModbusRtuFramer,
            port="/dev/ttyUSB0",
            baudrate=baud_rate,
            parity=parity,
            stopbits=stopbits,
            bytesize=bytesize,
            method='rtu'
        )
    
    # Start server in a separate thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Wait for timeout
    time.sleep(timeout_seconds)
    print(f"\n⏱️ Test Timeout ({timeout_seconds}s reached)", flush=True)
    sys.exit(0)


def sendData():
    baud_rate, parity, slave_id = configure_modbus()

    # Count Mode
    count_mode = int(input('''Count Mode:
    1. Single Register (16-bit)
    2. Double Register (32-bit)
Choose Count Mode: ''').strip())

    # Data Type
    data_type = input('''Data Type:
    float - 32-bit Float
    long  - 32-bit Integer
    uint  - 16-bit Unsigned Integer
Choose Data Type: ''').strip()

    # Register Address
    register_address = int(input("Enter the starting register address: ").strip())

    # Sample data
    sample_value = 220.0  # Replace with actual value if needed
    registers = build_registers(count_mode, data_type, register_address, sample_value)

    # Prepare context
    data_block = {register_address + i: reg for i, reg in enumerate(registers)}
    slave_ctx = ModbusSlaveContext(hr=ModbusSparseDataBlock(data_block))
    context = ModbusServerContext(slaves={slave_id: slave_ctx}, single=False)

    print(f"✅ Modbus server ready. Serving data at registers starting from {register_address}")
    start_modbus_server_with_timeout(context, baud_rate, parity, args.stopbits, args.bytesize, 30)


if __name__ == '__main__':
    args = parse_args()
    baud_rate = args.baud_rate
    parity = args.parity
    slave_id = args.slave_id
    register_address = args.register_address
    count_mode = args.count_mode
    data_type = args.data_type
    timeout_seconds = args.timeout
    register_value = args.register_value
    
    # Build registers
    registers = build_registers(count_mode, data_type, register_address, register_value)
    data_block = {register_address + i: reg for i, reg in enumerate(registers)}
    slave_ctx = ModbusSlaveContext(hr=ModbusSparseDataBlock(data_block))
    context = ModbusServerContext(slaves={slave_id: slave_ctx}, single=False)

    # Display configuration
    print("🚀 RS485 Transmission - Starting as Slave Device", flush=True)
    print(f"📡 Slave ID: {slave_id}", flush=True)
    print(f"📍 Register Address: {register_address}", flush=True)
    print(f"📊 Register Value: {register_value}", flush=True)
    print(f"⏱️  Timeout: {timeout_seconds}s", flush=True)
    print(f"✅ Server ready and listening...", flush=True)
    
    try:
        start_modbus_server_with_timeout(context, baud_rate, parity, args.stopbits, args.bytesize, timeout_seconds)
    except Exception as e:
        print(f"❌ Failed to start Modbus server: {e}", flush=True)
        sys.exit(1)

