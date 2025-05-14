#!/usr/bin/env python
"""
Baby Cry Detector - Main Module
-------------------------------
Entry point for the baby cry detection system.
Orchestrates the initialization and operation of all components.
"""

import gc
import time
from src.cry_detector import CryDetector
from src.display_manager import DisplayManager
from src.buzzer_control import BuzzerControl
from src.led_indicator import LedIndicator
from config import SAMPLING_INTERVAL, LED_PIN

def main():
    """
    Main function that initializes and runs the baby cry detection system.
    """
    # Initial memory cleanup
    try:
        gc.collect()
        print("Initial memory cleanup complete")
    except:
        pass
    
    # Initialize components
    print("\n----\nBaby Cry Detection System\n----\n")
    display = DisplayManager()
    buzzer = BuzzerControl()
    detector = CryDetector()
    led = LedIndicator()
    
    # Main monitoring loop
    try:
        while True:
            # Update display
            display.update("Monitorando", "som...")
            
            # Sample and analyze audio
            print("Sampling audio...")
            detector.sample_audio()
            is_crying, energy = detector.detect_cry()
                        
            # If crying detected, update display and play melody
            if is_crying:
                print(f"Choro detectado! ({energy=:.5f})")
                display.update("Choro", "detectado!")
                led.blink(duration=0.1, times=5)
                # buzzer.play_melody()
            else:
                print(f"Choro não detectado {energy:.5f}...")
            
            # Wait until next sampling interval
            time.sleep(SAMPLING_INTERVAL)
            
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")
        detector.cleanup()

if __name__ == "__main__":
    main()
