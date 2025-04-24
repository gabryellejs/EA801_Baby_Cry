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
SAMPLE_DURATION = 1  # seconds of data
SAMPLES = SAMPLE_FREQ * SAMPLE_DURATION  # Total samples to collect
SAMPLING_INTERVAL = 5  # Sample every 5 seconds

# Detection parameters
LOW_CUT = 400  # Lower frequency cutoff for baby cry (Hz)
HIGH_CUT = 6000  # Upper frequency cutoff for baby cry (Hz)

# Detection threshold (originally in voltage domain)
VOLTAGE_THRESHOLD = 0.0025  # Original voltage-based threshold
VREF = 3.3  # Reference voltage for ADC
MAX_ADC = 65535  # Max value for 16-bit ADC

# Convert voltage threshold to ADC domain
# Formula: ADC_threshold = (voltage_threshold / vref^2) * max_adc^2
ADC_ENERGY_THRESHOLD = VOLTAGE_THRESHOLD * (MAX_ADC / VREF) * (MAX_ADC / VREF)

# Status LED configuration
USE_STATUS_LED = True
LED_PIN = 25  # GPIO pin for status LED

# ======= Baby Cry Detection Algorithm (ADC Domain) =======

def design_bandpass_coefficients(low_freq, high_freq, sample_rate):
    """Design simple IIR bandpass filter coefficients"""
    # Normalize frequencies to Nyquist
    f1 = low_freq / (sample_rate / 2)
    f2 = high_freq / (sample_rate / 2)
    
    # Ensure frequencies are in valid range
    f1 = max(0.01, min(0.99, f1))
    f2 = max(f1 + 0.01, min(0.99, f2))
    
    # Simple coefficients for a 2nd order IIR bandpass
    q = 1.0  # Quality factor
    w0 = math.pi * (f1 + f2)  # Center frequency
    bw = math.pi * (f2 - f1)  # Bandwidth
    
    # Calculate filter coefficients
    alpha = math.sin(bw) / (2 * q)
    
    b0 = alpha
    b1 = 0
    b2 = -alpha
    a0 = 1 + alpha
    a1 = -2 * math.cos(w0)
    a2 = 1 - alpha
    
    # Normalize coefficients
    b = [b0/a0, b1/a0, b2/a0]
    a = [1.0, a1/a0, a2/a0]
    
    return (b, a)

def apply_bandpass_filter(data, b, a):
    """Apply IIR bandpass filter to ADC data (efficient memory usage)."""
    filtered = array.array('f')  # Start empty, append filtered values
    
    # Input and output history (2nd order filter)
    x1, x2 = 0.0, 0.0
    y1, y2 = 0.0, 0.0

    for x0 in data:
        # Apply difference equation
        y0 = (b[0] * x0 +
              b[1] * x1 +
              b[2] * x2 -
              a[1] * y1 -
              a[2] * y2)
        
        filtered.append(y0)

        # Update histories
        x2, x1 = x1, x0
        y2, y1 = y1, y0

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
    """Process ADC data directly and detect if baby crying is present"""
    # Design filter
    b, a = design_bandpass_coefficients(LOW_CUT, HIGH_CUT, SAMPLE_FREQ)
    
    # Apply filter - input is raw ADC values
    filtered_data = apply_bandpass_filter(adc_data, b, a)
    
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
        print(f"Monitoring using {LOW_CUT}-{HIGH_CUT}Hz band")
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
                
                # Report detection results
                if is_crying:
                    detection_count += 1
                    print(f"[{time_str}] 🚨 BABY CRYING DETECTED! 🚨 (Energy: {energy:.2f})")
                    print(f"Detection #{detection_count}")
                else:
                    print(f"[{time_str}] No cry detected (Energy: {energy:.2f})")
                
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
        
    # Create and configure sampler
    sampler = MicrophoneSampler()
    sampler.init_adc()
    
    # Start the main loop
    sampler.run()

if __name__ == "__main__":
    main()