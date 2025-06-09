#!/usr/bin/env python
"""
Cry Detector Module
------------------
Handles microphone sampling and baby cry 
detection using digital signal processing.
"""
import gc
import time
import array
import utime
from machine import Pin, ADC
from src.audio_processing import apply_bandpass_filter, calculate_energy
from config import (
    MIC_PIN, SAMPLE_FREQ, SAMPLES, LED_PIN,
    ADC_ENERGY_THRESHOLD, VREF, MAX_ADC, SAMPLING_INTERVAL
)

class CryDetector:
    """
    Class for sampling audio and detecting baby cries.
    """
    
    def __init__(self, threshold):
        """Initialize the cry detector with ADC and status LED."""
        # Initialize ADC for microphone
        self.adc = ADC(Pin(MIC_PIN))
        
        # Buffer for storing audio samples (16-bit unsigned)
        self.adc_buffer = array.array('H', [0] * SAMPLES)
        
        # Calculate microseconds between samples
        self.sample_interval_us = 1000000 // SAMPLE_FREQ
        
        # Initialize status LED
        self.led = Pin(LED_PIN, Pin.OUT)
        self.led.value(0)  # Ensure LED is off
        
        self.threshold = threshold
        
        print("Cry detector initialized")
        
    def sample_audio(self):
        """
        Sample audio from the microphone at the target frequency.
        Stores samples in the adc_buffer.
        
        Returns:
            Actual duration of sampling in seconds
        """
        start_time = utime.ticks_us()
        next_sample_time = start_time
        
        # Take samples at regular intervals to maintain sampling frequency
        for i in range(SAMPLES):
            # Wait until it's time for the next sample
            current_time = utime.ticks_us()
            if utime.ticks_diff(next_sample_time, current_time) > 0:
                # If we're ahead of schedule, wait
                utime.sleep_us(utime.ticks_diff(next_sample_time, current_time))
            
            # Take the sample
            self.adc_buffer[i] = self.adc.read_u16()
            
            # Calculate next sample time
            next_sample_time = utime.ticks_add(start_time, (i + 1) * self.sample_interval_us)
        
        # Calculate actual duration
        actual_duration = utime.ticks_diff(utime.ticks_us(), start_time) / 1000000
        return actual_duration
    
    def detect_cry(self):
        """
        Process audio data to detect if baby crying is present.
        
        Returns:
            Tuple of (is_crying, energy)
        """
        # Apply bandpass filter to the audio data
        filtered_data = apply_bandpass_filter(self.adc_buffer)
        
        # Calculate energy of the filtered signal
        energy = calculate_energy(filtered_data)
        
        # Convert to voltage domain for reporting (optional)
        voltage_energy = energy * (VREF / MAX_ADC)**2
            
        print(f"Comparing with threshold = {self.threshold}")
            
        # Determine if crying based on energy threshold
        is_crying = voltage_energy > self.threshold
        
        return is_crying, voltage_energy
    
    def set_threshold(self, threshold):
        self.threshold = threshold
    
    def get_threshold(self):
        return self.threshold
    
    def cleanup(self):
        """Clean up resources when detection is stopped."""
        self.led.value(0)  # Ensure LED is off
