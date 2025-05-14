from machine import Pin
import utime
from config import LED_PIN

class LedIndicator:
    """
    Controls a simple LED indicator.
    """

    def __init__(self):
        """Initialize the LED pin as output and turn it off."""
        self.led = Pin(LED_PIN, Pin.OUT)
        self.led.value(0)  # Off by default
        print("LED indicator initialized")

    def blink(self, duration_ms=100, times=5):
        """
        Blink the LED once for a given duration.

        Args:
            duration (float): Time in seconds to keep the LED on.
        """
        for _ in range(times):
            self.led.value(1)
            utime.sleep_ms(duration_ms)
            self.led.value(0)
            utime.sleep_ms(duration_ms)

    def stop(self):
        """
        Turn off the LED.
        """
        self.led.value(0)


