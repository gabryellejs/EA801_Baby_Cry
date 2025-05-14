#!/usr/bin/env python
"""
Buzzer Control Module
-------------------
Manages the buzzer for playing melodies when baby crying is detected.
"""

import time
from machine import Pin, PWM
from config import BUZZER_PIN, BUTTON_PIN, MUSIC_VOLUME, NOTES, MELODY

class BuzzerControl:
    """
    Class for controlling the buzzer and playing melodies.
    """
    
    def __init__(self):
        """Initialize the buzzer and stop button."""
        # Initialize buzzer with PWM
        self.buzzer = PWM(Pin(BUZZER_PIN))
        self.buzzer.duty_u16(0)  # Start with buzzer off
        
        # Initialize button for stopping melody
        self.button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)
        
        print("Buzzer controller initialized")
    
    def play_note(self, note, duration):
        """
        Play a single note on the buzzer.
        
        Args:
            note: Note name (e.g., "C4")
            duration: Duration in seconds
            
        Returns:
            Boolean indicating if note played completely (False if interrupted)
        """
        if note in NOTES:
            # Set frequency for the note
            self.buzzer.freq(NOTES[note])
            
            # Turn on buzzer
            BUZZER_VOLUME = int((MUSIC_VOLUME / 100) * 65535)
            self.buzzer.duty_u16(BUZZER_VOLUME)
            
            # Wait for duration or until button press
            start_time = time.ticks_ms()
            while time.ticks_diff(time.ticks_ms(), start_time) < duration * 1000:
                # Check if button pressed (active low)
                if self.button.value() == 0:
                    self.buzzer.duty_u16(0)  # Turn off buzzer
                    return False
                    
            # Turn off buzzer
            self.buzzer.duty_u16(0)
            
            # Small pause between notes
            time.sleep(0.01)
            
        return True
    
    def play_melody(self):
        """
        Play the melody defined in the configuration.
        Can be interrupted by button press.
        """
        print("Playing melody...")
        
        for note, duration in MELODY:
            # Play note and check if interrupted
            if not self.play_note(note, duration):
                print("Melody interrupted")
                break
