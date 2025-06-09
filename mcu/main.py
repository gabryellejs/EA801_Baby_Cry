#!/usr/bin/env python
import gc
import time
from machine import Pin
from src.cry_detector import CryDetector
from src.display_manager import DisplayManager
from src.buzzer_control import BuzzerControl
from src.led_indicator import LedIndicator
from src.bluetooth_interface import BluetoothInterface
from src.pushover_client import PushoverClient

from config import (
    SAMPLING_INTERVAL, 
    LED_PIN, 
    MUSIC_VOLUME,
    SSID,
    PASSWORD,
    PUSHOVER_USER_KEY,
    PUSHOVER_API_TOKEN,
    VOLTAGE_THRESHOLD,
    BUTTON_PIN
)

def main():
    gc.collect()
    print("Inicializando sistema de detecção de choro...\n")

    display = DisplayManager()
    buzzer = BuzzerControl()
    detector = CryDetector(VOLTAGE_THRESHOLD)
    led = LedIndicator()
    client = PushoverClient(
        SSID, 
        PASSWORD, 
        PUSHOVER_USER_KEY, 
        PUSHOVER_API_TOKEN
    )
    
    # Initialize button
    button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)
    
    sistema_ativo = True
    volume = MUSIC_VOLUME

    display.update("Conectando", "Wi-Fi...")
    client.connect_wifi()

    try:
        calibration_flag = 0
        calibration_counter = 0
        calibration_size = 3
        calibration_threshold = detector.get_threshold()
        while True:
            
            detector.sample_audio()
            is_crying, energy = detector.detect_cry()
            
            # Check for button press to trigger calibration
            if button.value() == 0:  # Button pressed (active low)
                press_start = time.ticks_ms()
                while button.value() == 0:  # Wait until button is released
                    if time.ticks_diff(time.ticks_ms(), press_start) >= 2000:  # 2 seconds
                        display.update("Calibrando", "aguarde...")
                        calibration_flag = 1
                        break
                # Wait for button release if not already released
                while button.value() == 0:
                    pass
            
            if calibration_flag:
                calibration_threshold += energy
                calibration_counter += 1
                
                if calibration_counter > calibration_size:
                    display.update("Calibração", "finalizada")
                    new_threshold = calibration_threshold / calibration_size
                    detector.set_threshold(new_threshold)
                    calibration_flag = 0
                    
                continue
            
            display.update("Monitorando", "som...")
            
            if is_crying:
                print(f"Choro detectado! ({energy=:.5f})")
                display.update("Choro", "detectado!")
                led.blink(duration_ms=100, times=5)
                # buzzer.play_melody()
                client.send_notification("Choro detectado!")
            else:
                print(f"Sem choro ({energy:.5f})")
            time.sleep(SAMPLING_INTERVAL)
    except KeyboardInterrupt:
        print("\nEncerrado pelo usuário.")
        detector.cleanup()

if __name__ == "__main__":
    main()
