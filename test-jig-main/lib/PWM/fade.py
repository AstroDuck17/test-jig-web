import RPi.GPIO as GPIO
import time

# Global to track existing PWM fader
_led_fader_instance = None

class LedFader:
    def __init__(self, pin, frequency=1000, device_connected=False):
        global _led_fader_instance
        if _led_fader_instance is not None:
            _led_fader_instance.cleanup()  # cleanup previous instance
        _led_fader_instance = self
        self.pin = pin
        self.frequency = frequency
        self.device_connected = device_connected  # new flag to track connection
        
        # Set up GPIO and try to release previous channel if needed
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        try:
            GPIO.setup(self.pin, GPIO.OUT)
        except RuntimeError:
            GPIO.cleanup(self.pin)
            GPIO.setup(self.pin, GPIO.OUT)
        
        # Set up PWM
        self.pwm = GPIO.PWM(self.pin, self.frequency)
        self.pwm.start(0)  # Start PWM with 0% duty cycle (off)

    def fade_in(self, speed=0.02):
        for duty_cycle in range(0, 101, 1):
            self.pwm.ChangeDutyCycle(duty_cycle)
            if self.device_connected:
                # Only print if device is connected
                print(f"duty cycle :{duty_cycle}%")
            time.sleep(speed)

    def fade_out(self, speed=0.02):
        for duty_cycle in range(100, -1, -1):
            self.pwm.ChangeDutyCycle(duty_cycle)
            if self.device_connected:
                # Only print if device is connected
                print(f"duty cycle :{duty_cycle}%")
            time.sleep(speed)

    def activate_gui(self, speed=0.05):
        try:
            while True:
                self.fade_in(speed)
                self.fade_out(speed)
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()

    def activate_cli(self, speed=0.05):
        try:
            while True:
                self.fade_in(speed)
                self.fade_out(speed)
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()

    def cleanup(self):
        self.pwm.stop()
        GPIO.cleanup()

# Example usage
if __name__ == "__main__":
    led_pin = 18  # Change this to your desired GPIO pin
    fader = LedFader(led_pin)
    fader.activate()
