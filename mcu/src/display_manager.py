#!/usr/bin/env python
"""
Display Manager Module
--------------------
Handles the OLED display for the baby cry detector.
"""

from machine import Pin, SoftI2C
from lib.ssd1306 import SSD1306_I2C
from config import I2C_SCL_PIN, I2C_SDA_PIN, OLED_WIDTH, OLED_HEIGHT

class DisplayManager:
    """
    Class for managing the OLED display.
    Handles display initialization and text updating.
    """
    
    def __init__(self):
        """Initialize the OLED display with I2C interface."""
        # Initialize I2C for OLED display
        i2c_oled = SoftI2C(scl=Pin(I2C_SCL_PIN), sda=Pin(I2C_SDA_PIN))
        
        # Initialize OLED display
        try:
            self.oled = SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, i2c_oled)
            self.display_active = True
            self.update("Sistema", "iniciado")
            print("Display initialized")
        except Exception as e:
            self.display_active = False
            print(f"Failed to initialize display: {e}")
    
    def update(self, line1="", line2=""):
        """
        Update the display with new text.
        
        Args:
            line1: Text for the first line
            line2: Text for the second line
        """
        if not self.display_active:
            return
            
        try:
            # Clear display
            self.oled.fill(0)
            
            # Write text centered on lines
            self.oled.text(line1, 0, 20)
            self.oled.text(line2, 0, 35)
            
            # Update display
            self.oled.show()
        except Exception as e:
            print(f"Display update error: {e}")
            self.display_active = False