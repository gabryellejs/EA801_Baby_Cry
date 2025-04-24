"""
Sample Rate      | Purpose
8 kHz            | Telephony, voice-only (e.g., VoIP, phone calls) — captures up to 4 kHz
16 kHz           | Better quality speech processing (e.g., voice assistants, ASR) — captures up to 8 kHz
22.05 kHz        | Intermediate audio quality, some music
44.1 kHz         | Standard for music/audio CDs — captures up to 22.05 kHz
48 kHz           | Professional audio/video production — common in digital media
96 kHz / 192 kHz | High-resolution audio — for studio or scientific use
"""


import time
import array
import struct
import os
from machine import Pin, ADC
import utime

# Microphone parameters
MIC_CHANNEL = 2
MIC_PIN = 26 + MIC_CHANNEL  # GPIO 28 for ADC channel 2

# Sampling parameters
SAMPLE_FREQ = 16000  # 16kHz sampling frequency
SAMPLE_DURATION = 2  # seconds of data
SAMPLES = SAMPLE_FREQ * SAMPLE_DURATION  # Total samples to collect
SAMPLING_INTERVAL = 10  # Sample every 10 seconds

# File configuration
DATA_DIR = "mic_data"  # Directory to store binary files
INDEX_FILE = "recordings.txt"  # File to track recordings with timestamps
LABEL = "dog"

def ensure_data_dir():
    """Create data directory if it doesn't exist"""
    try:
        os.mkdir(DATA_DIR)
    except OSError:
        # Directory already exists
        pass

def get_datetime():
    """Get current datetime as a string"""
    now = utime.localtime()
    return "{:04d}-{:02d}-{:02d}_{:02d}-{:02d}-{:02d}".format(
        now[0], now[1], now[2],  # Year, month, day
        now[3], now[4], now[5]   # Hour, minute, second
    )

def append_to_index(binary_file, timestamp):
    """Add recording info to index file"""
    try:
        with open(INDEX_FILE, 'a') as f:
            f.write(f"{timestamp},{binary_file},{SAMPLE_FREQ},{SAMPLES}\n")
    except OSError:
        print("Warning: Could not update index file")

class MicrophoneSampler:
    def __init__(self):
        self.adc_buffer = array.array('H', [0] * SAMPLES)  # 16-bit unsigned values
        self.adc = None
        self.sample_interval_us = 1000000 // SAMPLE_FREQ  # Microseconds between samples
        
    def init_adc(self):
        """Initialize the ADC for microphone reading"""
        print("Preparing ADC...")
        self.adc = ADC(Pin(MIC_PIN))
        print("ADC configured!")
        
    def sample_mic(self):
        """Sample the microphone at the target frequency"""
        print(f"Sampling microphone for {SAMPLE_DURATION} seconds at {SAMPLE_FREQ}Hz...")
        
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
        print(f"Sampling complete. Actual duration: {actual_duration:.3f} seconds")
        
        return actual_duration
    
    def save_binary_file(self, timestamp):
        """Save the buffer as raw binary data"""
        filename = f"{DATA_DIR}/{SAMPLE_FREQ}Hz_{SAMPLE_DURATION}s_each_{SAMPLING_INTERVAL}s-{timestamp}_{LABEL}.bin"
        
        print(f"Saving raw data to {filename}...")
        
        try:
            with open(filename, 'wb') as f:
                # Write raw binary data directly from the array
                f.write(self.adc_buffer)
                
            print(f"Binary data saved successfully to {filename}")
            return filename
        except Exception as e:
            print(f"Error saving binary data: {e}")
            return None

    def run(self):
        """Main loop for the microphone sampler"""
        print("\n----\nStarting microphone sampling loop...\n----\n")
        
        ensure_data_dir()
        
        # Create index file if it doesn't exist
        try:
            with open(INDEX_FILE, 'r'):
                pass
        except OSError:
            with open(INDEX_FILE, 'w') as f:
                f.write("timestamp,filename,sample_rate,num_samples\n")
        
        try:
            while True:
                # Get timestamp before sampling
                timestamp = get_datetime()
                print(f"Starting measurement at {timestamp}")
                
                # Sample the microphone
                actual_duration = self.sample_mic()
                
                # Save binary data
                binary_file = self.save_binary_file(timestamp)
                
                if binary_file:
                    # Update index file
                    append_to_index(binary_file, timestamp)
                    
                    # Calculate file size and show info
                    try:
                        file_stats = os.stat(binary_file)
                        file_size_kb = file_stats[6] / 1024
                        print(f"Binary file size: {file_size_kb:.1f} KB")
                    except:
                        pass
                
                # Wait until next sampling interval
                print(f"Waiting {SAMPLING_INTERVAL} seconds until next sample...")
                time.sleep(SAMPLING_INTERVAL)
                
        except KeyboardInterrupt:
            print("\nSampling stopped by user.")
            
def main():
    # Wait for serial monitor to open
    print("Initializing microphone sampler...")
    time.sleep(1)
    
    # Create conversion script
    # create_conversion_script()
    
    # Create and configure sampler
    sampler = MicrophoneSampler()
    sampler.init_adc()
    
    # Start the main loop
    sampler.run()

if __name__ == "__main__":
    main()
