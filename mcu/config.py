#!/usr/bin/env python
"""
Configuration Module for Baby Cry Detector
-----------------------------------------
Centralizes all configuration parameters and constants for the system.
"""

# ======= GPIO Configuration =======
# LED for status indication
LED_PIN = 13
# Buzzer pin
BUZZER_PIN = 21
# Button pin (for stopping melody)
BUTTON_PIN = 5
# I2C pins for OLED display
I2C_SCL_PIN = 15
I2C_SDA_PIN = 14

# ======= Display Configuration =======
OLED_WIDTH = 128
OLED_HEIGHT = 64

# ======= Microphone Configuration =======
# ADC channel and pin for microphone
MIC_CHANNEL = 2
MIC_PIN = 26 + MIC_CHANNEL  # GPIO 28 for ADC channel 2

# ======= Sampling Parameters =======
# Sampling frequency in Hz
SAMPLE_FREQ = 16000
# Duration of each sample in seconds
SAMPLE_DURATION = 1
# Total number of samples to collect
SAMPLES = SAMPLE_FREQ * SAMPLE_DURATION
# Interval between sampling sessions in seconds
SAMPLING_INTERVAL = 2

# ======= Detection Parameters =======
# Reference voltage for ADC
VREF = 3.3
# Maximum value for 16-bit ADC
MAX_ADC = 65535
# Threshold for cry detection (voltage domain)
VOLTAGE_THRESHOLD = 1e-3 # 9e-4
# Convert voltage threshold to ADC domain
ADC_ENERGY_THRESHOLD = VOLTAGE_THRESHOLD * (MAX_ADC / VREF) * (MAX_ADC / VREF)

# ======= Filter Parameters =======
# Pre-computed filter coefficients for bandpass filter (4500-6000 Hz)
FILTER_A = [1.0, 0.8695831964878592, 0.5652084017560705]
FILTER_B = [0.2173957991219648, 0.0, -0.2173957991219648]

# ======= Buzzer Parameters =======
# Volume from 0 to 100%
MUSIC_VOLUME = 1

# ======= Musical Notes =======
NOTES = {
    "C4": 262, "D4": 294, "E4": 330, "F4": 349,
    "G4": 392, "A4": 440, "B4": 494, "C5": 523
}

# Melody pattern (note, duration in seconds)
MELODY = [
    ("C4", 0.5), ("D4", 0.5), ("E4", 0.5), ("F4", 0.5), ("G4", 0.5),
    ("G4", 0.5), ("A4", 0.5), ("G4", 1.0), ("G4", 0.5), ("F4", 0.5),
    ("E4", 0.5), ("D4", 0.5), ("E4", 0.5), ("F4", 0.5), ("G4", 1.0),
    ("C4", 0.5), ("D4", 0.5), ("E4", 0.5), ("F4", 0.5), ("G4", 0.5),
    ("G4", 0.5), ("A4", 0.5), ("G4", 1.0), ("G4", 0.5), ("F4", 0.5),
    ("E4", 0.5), ("D4", 0.5), ("C4", 0.5), ("C4", 1.0)
]

# ======= Wi-Fi Pushover config =======
SSID = "iPhone de Gabriel"
PASSWORD = "12345678"
PUSHOVER_USER_KEY = "uciyd2qp7bt5bzwhggcp5ir8qihgwi"
PUSHOVER_API_TOKEN = "abpbk6nwqf2bba9ze5mfzrfuyuibc2"
