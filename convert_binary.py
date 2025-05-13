# Binary to WAV/CSV conversion script
# Save this on your computer to convert the binary files

import os
import sys
import struct
import wave
import csv
import numpy as np
from datetime import datetime

def read_index_file(index_path):
    """Read the recordings index file"""
    recordings = []
    with open(index_path, 'r') as f:
        next(f)  # Skip header
        for line in f:
            parts = line.strip().split(',')
            if len(parts) >= 4:
                recordings.append({
                    'timestamp': parts[0],
                    'filename': parts[1],
                    'sample_rate': int(parts[2]),
                    'num_samples': int(parts[3])
                })
    return recordings

def binary_to_wav(binary_path, wav_path, sample_rate=16000):
    """Convert raw binary file to WAV format"""
    with open(binary_path, 'rb') as bin_file:
        # Read binary data (16-bit unsigned integers)
        data = bin_file.read()
        
    # Create a wave file
    with wave.open(wav_path, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 2 bytes per sample (16-bit)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(data)
    
    print(f"Converted {binary_path} to {wav_path}")

def binary_to_csv(binary_path, csv_path, sample_rate=16000):
    """Convert raw binary file to CSV format"""
    # Read binary data as 16-bit unsigned integers
    values = []
    with open(binary_path, 'rb') as bin_file:
        data = bin_file.read()
        # Unpack as 16-bit unsigned integers
        values = struct.unpack(f"<{len(data)//2}H", data)
    
    # Calculate time for each sample
    times = [i/sample_rate for i in range(len(values))]
    
    # Write to CSV
    with open(csv_path, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['sample_num', 'time_sec', 'adc_value', 'voltage'])
        
        for i, (time, value) in enumerate(zip(times, values)):
            voltage = value * 3.3 / 65535  # Convert to voltage
            writer.writerow([i, f"{time:.6f}", value, f"{voltage:.6f}"])
    
    print(f"Converted {binary_path} to {csv_path}")

def process_all_recordings(data_dir, index_path, output_dir):
    """Process all recordings listed in the index file"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    recordings = read_index_file(index_path)
    
    for rec in recordings:
        binary_path = os.path.join(data_dir, os.path.basename(rec['filename']))
        if not os.path.exists(binary_path):
            print(f"Warning: Could not find {binary_path}")
            continue
            
        base_name = os.path.splitext(os.path.basename(binary_path))[0]
        wav_path = os.path.join(output_dir, f"{base_name}.wav")
        csv_path = os.path.join(output_dir, f"{base_name}.csv")
        
        # Convert to WAV
        binary_to_wav(binary_path, wav_path, rec['sample_rate'])
        
        # Convert to CSV
        binary_to_csv(binary_path, csv_path, rec['sample_rate'])

if __name__ == "__main__":
    # Set these paths to match your setup
    DATA_DIR = "data/mic_data/new_mcu"           # Directory with binary files
    INDEX_FILE = "new_mcu_recordings.txt"   # Recording index file
    OUTPUT_DIR = "data/converted_data/new_mcu"   # Where to save WAV and CSV files
    
    if len(sys.argv) > 1:
        # Process specific file if provided
        binary_file = sys.argv[1]
        base_name = os.path.splitext(os.path.basename(binary_file))[0]
                
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
            
        binary_to_wav(binary_file, f"{OUTPUT_DIR}/{base_name}.wav")
        binary_to_csv(binary_file, f"{OUTPUT_DIR}/{base_name}.csv")
    else:
        # Process all files
        process_all_recordings(DATA_DIR, INDEX_FILE, OUTPUT_DIR)
        print(f"All files processed. Results saved in {OUTPUT_DIR}")