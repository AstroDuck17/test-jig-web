#!/usr/bin/env python3
import time
import argparse
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian

def parse_args():
    parser = argparse.ArgumentParser(description="RS485 Receive Test")
    parser.add_argument("--baud_rate", type=int, default=9600, help="Baud rate")
    parser.add_argument("--parity", type=str, default="E", help="Parity bit")
    parser.add_argument("--slave_id", type=int, default=1, help="Slave ID")
    parser.add_argument("--register_address", type=int, required=True, help="Register Address")
    # Add stopbits and bytesize arguments
    parser.add_argument("--stopbits", type=int, choices=[1,2], default=1, help="Stopbits, 1 or 2")
    parser.add_argument("--bytesize", type=int, choices=[7,8], default=8, help="Bytesize, 7 or 8")
    parser.add_argument("--scaling_factor", type=float, default=1.0, help="Scaling factor for output value")
    return parser.parse_args()

def config(args):
    baud_rate = args.baud_rate
    parity = args.parity
    slave_id = args.slave_id
    client = ModbusClient(
        method='rtu',
        port="/dev/ttyUSB0",
        baudrate=baud_rate,
        parity=parity,
        stopbits=args.stopbits,   # use argument
        bytesize=args.bytesize,   # use argument
        timeout=1
    )
    if not client.connect():
        print("❌ Failed to open serial port. Check USB and permissions.", flush=True)
        exit(1)
    else:
        print("✅ Connected successfully.", flush=True)
    return client, slave_id

def read_modbus_values(client, slave_id, register_address, scaling_factor=1.0):
    try:
        while True:
            rr = client.read_holding_registers(address=register_address, count=2, unit=slave_id)
            if rr.isError():
                print(f"❌ Error while fetching data from register {register_address}", flush=True)
            else:
                regs = rr.registers
                decoder = BinaryPayloadDecoder.fromRegisters(
                    regs,
                    byteorder=Endian.Big,
                    wordorder=Endian.Little
                )
                value = round(decoder.decode_32bit_float() * scaling_factor, 3)
                print(f"Register {register_address}: {value}", flush=True)
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting RS485 Receive Test.", flush=True)

if __name__ == "__main__":
    args = parse_args()
    client, slave_id = config(args)
    read_modbus_values(client, slave_id, args.register_address, args.scaling_factor)
    client.close()
    #         if rr.isError():
    #             print(f"❌ Error while fetching data from register {addr}")
    #             continue  # Prompt again if there's an error
            
    #         regs = rr.registers
    #         decoder = BinaryPayloadDecoder.fromRegisters(
    #             regs,
    #             byteorder=Endian.Big,     # bytes are big-endian
    #             wordorder=Endian.Little   # words are swapped
    #         )
    #         value = round(decoder.decode_32bit_float(), 3)
    #         print(f"\nRegister {addr}: {value}")

    # except KeyboardInterrupt:
    #     print("\n\nExiting register reader. Goodbye! 👋")

    

# if __name__ == "__main__":


#     meter_ids = [1]
#     for mid in meter_ids:
#         print(f"\nReading Meter #{mid}")
#         data = read_modbus_values(mid, client)
#         for name, val in data.items():
#             print(f"  {name:10s}: {val}")
#         time.sleep(0.2)   # small pause

#     client.close()
#     print("\nAll done.")
