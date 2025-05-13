# New version of the identification code for the MCU

import array
import math
from machine import Pin, ADC
import utime
import time

# ======= Configuration Parameters =======

# Microphone parameters
MIC_CHANNEL = 2
MIC_PIN = 26 + MIC_CHANNEL  # GPIO 28 for ADC channel 2

# Sampling parameters
SAMPLE_FREQ = 16000  # 16kHz sampling frequency
SAMPLE_DURATION = 2  # seconds of data
SAMPLES = SAMPLE_FREQ * SAMPLE_DURATION  # Total samples to collect
SAMPLING_INTERVAL = 3  # Sample every 5 seconds

# Detection threshold (originally in voltage domain)
VOLTAGE_THRESHOLD = 9e-4  # Original voltage-based threshold
VREF = 3.3  # Reference voltage for ADC
MAX_ADC = 65535  # Max value for 16-bit ADC

# Convert voltage threshold to ADC domain
# Formula: ADC_threshold = (voltage_threshold / vref^2) * max_adc^2
ADC_ENERGY_THRESHOLD = VOLTAGE_THRESHOLD * (MAX_ADC / VREF) * (MAX_ADC / VREF)

# Status LED configuration
USE_STATUS_LED = True
LED_PIN = 25  # GPIO pin for status LED

# ======= Hardcoded Filter Constants =======

# Pre-computed filter coefficients for the bandpass filter
# This eliminates the need to compute them at runtime

# 4500 - 6000 Hz
FILTER_A = [1.0, 0.8695831964878592, 0.5652084017560705]
FILTER_B = [0.2173957991219648, 0.0, -0.2173957991219648]

# ======= Baby Cry Detection Algorithm (ADC Domain) =======

def apply_df2_bandpass_filter(data):
    """
    Direct Form II IIR bandpass filter implementation
    Uses only 2 state variables instead of 4
    """
    filtered = array.array('f', data) if isinstance(data, array.array) else array.array('f', data)
    
    # Direct Form II uses only two state variables
    w1 = w2 = 0.0
    
    # Pre-fetch coefficients
    b0, b1, b2 = FILTER_B[0], FILTER_B[1], FILTER_B[2]
    a1, a2 = FILTER_A[1], FILTER_A[2]
    
    for i in range(len(filtered)):
        x0 = filtered[i]
        # Calculate intermediate value w0
        w0 = x0 - a1 * w1 - a2 * w2
        
        # Calculate output
        y0 = b0 * w0 + b1 * w1 + b2 * w2
        
        # Update state
        w2, w1 = w1, w0
        
        filtered[i] = y0
        
    return filtered

def calculate_energy(filtered_data):
    """Calculate energy directly from filtered data"""
    energy = 0
    for sample in filtered_data:
        energy += sample * sample
    
    # Normalize by signal length
    if len(filtered_data) > 0:
        energy /= len(filtered_data)
    
    return energy

def detect_baby_cry(adc_data):
    """
    Process ADC data directly and detect if baby crying is present
    
    Args:
        adc_data: Array of ADC samples
        filter_type: Type of filter to use ("iir", "light", or None)
    
    Returns:
        Tuple of (is_crying, energy)
    """
    # Apply filter
    filtered_data = apply_df2_bandpass_filter(adc_data)
    
    # Calculate energy
    energy = calculate_energy(filtered_data)
    
    # Use ADC-domain threshold for comparison
    is_crying = energy > ADC_ENERGY_THRESHOLD
    
    return is_crying, energy

# ======= Microphone Sampling Class =======

class MicrophoneSampler:
    def __init__(self):
        self.adc = None
        # Initialize with 'H' for 16-bit unsigned
        self.adc_buffer = array.array('H', [0] * SAMPLES)
        self.sample_interval_us = 1000000 // SAMPLE_FREQ  # Microseconds between samples
        
        # Initialize LED if enabled
        self.led = None
        if USE_STATUS_LED:
            self.led = Pin(LED_PIN, Pin.OUT)
            self.led.value(0)  # Turn off at start
        
    def init_adc(self):
        """Initialize the ADC for microphone reading"""
        print("Preparing ADC...")
        self.adc = ADC(Pin(MIC_PIN))
        print("ADC configured!")
        
    def sample_mic(self):
        """Sample the microphone at the target frequency"""
        print(f"Sampling microphone for {SAMPLE_DURATION} seconds...")
        
        start_time = utime.ticks_us()
        next_sample_time = start_time
        
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
        
        actual_duration = utime.ticks_diff(utime.ticks_us(), start_time) / 1000000
        return actual_duration
    
    def signal_detection(self, is_crying):
        """Signal detection status with LED (if enabled)"""
        if not USE_STATUS_LED or not self.led:
            return
            
        if is_crying:
            # Blink rapidly for crying detection
            for _ in range(5):  # Reduced to 5 blinks to save time
                self.led.value(1)
                utime.sleep_ms(100)
                self.led.value(0)
                utime.sleep_ms(100)
        else:
            # Single blink for no detection
            self.led.value(1)
            utime.sleep_ms(200)
            self.led.value(0)

    def get_current_time(self):
        """Get current time as HH:MM:SS string"""
        now = utime.localtime()
        return "{:02d}:{:02d}:{:02d}".format(now[3], now[4], now[5])  # Hour, minute, second

    def run(self):
        """Main loop for microphone sampling and baby cry detection"""
        print("\n----\nBaby Cry Detection Monitor\n----\n")
        print(f"ADC Energy Threshold: {ADC_ENERGY_THRESHOLD}")
        print("Press Ctrl+C to stop monitoring\n")
        
        detection_count = 0
        gc_counter = 0  # Counter for garbage collection
        
        try:
            while True:
                # Sample the microphone
                time_str = self.get_current_time()
                print(f"[{time_str}] Listening...")
                self.sample_mic()
                
                # Process for baby cry detection
                detection_start = utime.ticks_ms()
                is_crying, energy = detect_baby_cry(self.adc_buffer)
                detection_time = utime.ticks_diff(utime.ticks_ms(), detection_start)
                
                voltage_enery = energy * (VREF / MAX_ADC)**2
                
                # Report detection results
                if is_crying:
                    detection_count += 1
                    print(f"[{time_str}] 🚨 BABY CRYING DETECTED! 🚨 (Energy: {voltage_enery:.5f})")
                    print(f"Detection #{detection_count}")
                else:
                    print(f"[{time_str}] No cry detected (Energy: {voltage_enery:.5f})")
                
                print(f"Processing time: {detection_time}ms")
                
                # Signal detection with LED
                self.signal_detection(is_crying)
                
                # Wait until next sampling interval
                wait_time = max(1, SAMPLING_INTERVAL - SAMPLE_DURATION)
                time.sleep(wait_time)
                
                # Memory management: force garbage collection every few iterations
                gc_counter += 1
                if gc_counter >= 5:
                    gc_counter = 0
                    try:
                        import gc
                        gc.collect()
                    except:
                        pass
                
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user.")
            if USE_STATUS_LED and self.led:
                self.led.value(0)  # Ensure LED is off when stopping
            
def main():
    # Optional: Try to free memory before starting
    try:
        import gc
        gc.collect()
        print("Initial memory cleanup complete")
    except:
        pass
        
    # Create and configure sampler with specified filter type
    sampler = MicrophoneSampler()
    sampler.init_adc()
    
    # Start the main loop
    sampler.run()

if __name__ == "__main__":
    main()
