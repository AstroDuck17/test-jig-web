import RPi.GPIO as GPIO
import adafruit_dht
import board
import time

class DHTSensor:
    def __init__(self, pin):
        self.pin = pin
        self.dht_device = adafruit_dht.DHT11(self.pin, use_pulseio=False)

    def activate_gui(self):
        attempts = 5
        for i in range(attempts):
            try:
                # Wait longer to allow sensor stabilization before each attempt
                time.sleep(3)
                temperature = self.dht_device.temperature
                humidity = self.dht_device.humidity
                if humidity is not None and temperature is not None:
                    return f'Temperature: {temperature:.1f}°C<br>Humidity: {humidity:.1f}%'
            except Exception as error:
                # Catch all exceptions and retry
                pass
        return 'Failed to get reading. Try again!'

    def activate_cli(self):
        try:
            while True:
                temperature = self.dht_device.temperature
                humidity = self.dht_device.humidity
                if humidity is not None and temperature is not None:
                    print(f'Temperature: {temperature:.1f}°C\nHumidity: {humidity:.1f}%')
                    time.sleep(1)   
                else:
                    print('Failed to get reading. Try again!')
                    time.sleep(1)   
        except RuntimeError as e:
            print('Failed to get reading. Try again!')
        except KeyboardInterrupt:
            print("exiting....")
        finally:
            time.sleep(1)        

    def cleanup(self):
        GPIO.cleanup()

if __name__ == "__main__":
    try:
        sensor = DHTSensor(pin=board.D13)
        data = sensor.activate()
        print(data)
    except KeyboardInterrupt:
        print("\nExiting program")
    finally:
        sensor.cleanup()
