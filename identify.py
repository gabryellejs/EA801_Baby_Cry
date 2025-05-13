# Baby Cry Detection Evaluation System
# Processes multiple CSV files and evaluates detection performance

import os

from filters import *

# Core detection module (to be embedded in microcontroller)
# =========================================================

def load_csv(filename):
    """Load voltage data from CSV file"""
    voltages = []
    try:
        with open(filename, 'r') as file:
            # Skip header
            file.readline()
            
            for line in file:
                # Parse CSV line and extract voltage (4th column)
                parts = line.strip().split(',')
                if len(parts) >= 4:
                    try:
                        voltage = float(parts[3])  # Assuming voltage is the 4th column
                        voltages.append(voltage)
                    except ValueError:
                        pass  # Skip lines with non-numeric voltage values
    except OSError as e:
        print(f"Error opening file: {e}")
    
    return voltages

def design_bandpass_coefficients(low_freq, high_freq, sample_rate):
    """
    Design simple IIR bandpass filter coefficients
    Returns (b, a) coefficients for the filter
    """
    import math
    
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

def calculate_energy(filtered_data):
    """Calculate energy of the filtered signal"""
    energy = 0
    for sample in filtered_data:
        energy += sample * sample
    
    # Normalize by signal length
    if len(filtered_data) > 0:
        energy /= len(filtered_data)
    
    return energy

def detect_baby_cry(data, sample_rate, low_cut, high_cut, threshold):
    """
    Core detection function - to be embedded in microcontroller
    Takes voltage data directly rather than a filename
    
    Returns:
    - is_crying: Boolean indicating if baby cry detected
    - energy: The computed signal energy for diagnostic purposes
    """
    # Design filter
    b, a = design_bandpass_coefficients(low_cut, high_cut, sample_rate)
    
    # print(f"Filter coefs:\n{a=}\n{b=}")
    
    # Apply filter
    filtered_data = apply_df2_bandpass_filter(data)
    
    # Calculate energy
    energy = calculate_energy(filtered_data)
    
    # Compare to threshold
    is_crying = energy > threshold
    
    return is_crying, energy

# Evaluation module (for desktop analysis)
# =======================================

def process_file(filename, sample_rate, low_cut, high_cut, threshold):
    """Process a single file and return detection result"""
    # Load data
    voltages = load_csv(filename)
    if not voltages:
        print(f"No data loaded from file: {filename}")
        return False, 0
    
    # Detect baby cry
    is_crying, energy = detect_baby_cry(voltages, sample_rate, low_cut, high_cut, threshold)
    
    return is_crying, energy

def get_ground_truth(filename, label='crying'):
    """Extract ground truth from filename"""
    base_name = os.path.basename(filename)
    return label in base_name

def get_audio_type(filename):
    """Determine the type of audio from filename"""
    base_name = os.path.basename(filename).lower()
    if 'baby' in base_name:
        return "baby"
    elif 'dog' in base_name or 'bark' in base_name:
        return "dog"
    elif 'silence' in base_name:
        return "silence"
    else:
        return "unknown"

def evaluate_performance(results):
    """Calculate performance metrics from results"""
    true_positives = 0
    false_positives = 0
    true_negatives = 0
    false_negatives = 0
    
    # Count for false positives that are dog barking
    dog_barking_false_positives = 0
    
    for filename, ground_truth, prediction, energy, audio_type in results:
        if ground_truth and prediction:  # True positive
            true_positives += 1
        elif ground_truth and not prediction:  # False negative
            false_negatives += 1
        elif not ground_truth and prediction:  # False positive
            false_positives += 1
            # Check if false positive is a dog barking
            if audio_type == "dog":
                dog_barking_false_positives += 1
        else:  # True negative
            true_negatives += 1
    
    # Calculate metrics
    total = true_positives + false_positives + true_negatives + false_negatives
    accuracy = (true_positives + true_negatives) / total if total > 0 else 0
    
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    dog_barking_percentage = (dog_barking_false_positives / false_positives * 100) if false_positives > 0 else 0
    
    return {
        "total_files": total,
        "true_positives": true_positives,
        "false_positives": false_positives,
        "true_negatives": true_negatives,
        "false_negatives": false_negatives,
        "dog_barking_false_positives": dog_barking_false_positives,
        "dog_barking_percentage": dog_barking_percentage,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1
    }

def print_dataframe(results, metrics):
    """Print results in a dataframe-like format"""
    # Print header for results table
    print("\nEvaluation Results:")
    print("-" * 100)
    print(f"{'Filename':<30} | {'Ground Truth':<12} | {'Prediction':<12} | {'Energy':<10} | {'Audio Type':<10} | {'Result':<10}")
    print("-" * 100)
    
    # Print each file result
    for filename, ground_truth, prediction, energy, audio_type in results:
        base_name = os.path.basename(filename)
        result = "Correct" if ground_truth == prediction else "Incorrect"
        print(f"{base_name:<30} | {'Crying' if ground_truth else 'Not Crying':<12} | "
              f"{'Crying' if prediction else 'Not Crying':<12} | {energy:<10.6f} | {audio_type:<10} | {result:<10}")
    
    # Print metrics
    print("\nPerformance Metrics:")
    print("-" * 60)
    print(f"Total Files: {metrics['total_files']}")
    print(f"True Positives: {metrics['true_positives']}")
    print(f"False Positives: {metrics['false_positives']}")
    print(f"  - Dog Barking False Positives: {metrics['dog_barking_false_positives']} ({metrics['dog_barking_percentage']:.2f}%)")
    print(f"True Negatives: {metrics['true_negatives']}")
    print(f"False Negatives: {metrics['false_negatives']}")
    print(f"Accuracy: {metrics['accuracy']:.4f}")
    print(f"Precision: {metrics['precision']:.4f}")
    print(f"Recall: {metrics['recall']:.4f}")
    print(f"F1 Score: {metrics['f1_score']:.4f}")
    
    # Print confusion matrix
    print("\nConfusion Matrix:")
    print("-" * 40)
    print(f"                | Predicted Crying | Predicted Not Crying")
    print(f"Actually Crying | {metrics['true_positives']:<16} | {metrics['false_negatives']:<20}")
    print(f"Actually Not    | {metrics['false_positives']:<16} | {metrics['true_negatives']:<20}")
    
    # Print dog barking analysis
    print("\nDog Barking Analysis:")
    print("-" * 40)
    print(f"Total False Positives: {metrics['false_positives']}")
    print(f"Dog Barking False Positives: {metrics['dog_barking_false_positives']}")
    print(f"Percentage of False Positives that are Dog Barking: {metrics['dog_barking_percentage']:.2f}%")

def save_results_to_csv(results, metrics, output_file="evaluation_results.csv"):
    """Save evaluation results to CSV file"""
    try:
        with open(output_file, 'w') as f:
            # Write header
            f.write("filename,ground_truth,prediction,energy,audio_type,result\n")
            
            # Write results
            for filename, ground_truth, prediction, energy, audio_type in results:
                base_name = os.path.basename(filename)
                result = "Correct" if ground_truth == prediction else "Incorrect"
                f.write(f"{base_name},{ground_truth},{prediction},{energy},{audio_type},{result}\n")
            
            # Write metrics
            f.write("\nMetrics\n")
            for key, value in metrics.items():
                f.write(f"{key},{value}\n")
            
            # Write dog barking specific analysis
            f.write("\nDog Barking Analysis\n")
            f.write(f"dog_barking_false_positives,{metrics['dog_barking_false_positives']}\n")
            f.write(f"dog_barking_percentage,{metrics['dog_barking_percentage']}\n")
                
        print(f"\nResults saved to {output_file}")
        
    except Exception as e:
        print(f"Error saving results: {e}")

def main():
    # Configuration Parameters
    DATA_FOLDER = "data/converted_data/new_mcu"  # Folder containing CSV files
    SAMPLE_RATE = 16000  # 16kHz
    LOW_CUT = 4500  # Lower frequency cutoff for baby cry (Hz)
    HIGH_CUT = 6000  # Upper frequency cutoff for baby cry (Hz)
    VOLTAGE_THRESHOLD = 7.9e-4  # Threshold for classification
    TP_LABEL = 'baby'
    
    print("Baby Cry Detection Evaluation System")
    print("===================================")
    
    # Get list of CSV files in folder
    try:
        files = [os.path.join(DATA_FOLDER, f) for f in os.listdir(DATA_FOLDER) if f.endswith('.csv')]
    except OSError:
        print(f"Error: Could not access folder {DATA_FOLDER}")
        return
    
    if not files:
        print(f"No CSV files found in {DATA_FOLDER}")
        return
    
    print(f"Found {len(files)} CSV files for processing")
    
    # Process each file
    results = []
    for i, filename in enumerate(files):
        print(f"\nProcessing file {i+1}/{len(files)}: {os.path.basename(filename)}")
        
        # Get ground truth from filename
        ground_truth = get_ground_truth(filename, label=TP_LABEL)
        
        # Get audio type
        audio_type = get_audio_type(filename)
        
        # Process file
        #start_time = utime.ticks_ms()
        prediction, energy = process_file(filename, SAMPLE_RATE, LOW_CUT, HIGH_CUT, VOLTAGE_THRESHOLD)
        #elapsed_time = utime.ticks_diff(utime.ticks_ms(), start_time)
        
        print(f"  Ground Truth: {'Crying' if ground_truth else 'Not Crying'}")
        print(f"  Prediction: {'Crying' if prediction else 'Not Crying'}")
        print(f"  Audio Type: {audio_type}")
        print(f"  Energy: {energy:.6f}")
        #print(f"  Time: {elapsed_time} ms")
        
        # Store result
        results.append((filename, ground_truth, prediction, energy, audio_type))
    
    # Calculate performance metrics
    metrics = evaluate_performance(results)
    
    # Print results
    print_dataframe(results, metrics)
    
    # Save results to CSV
    save_results_to_csv(results, metrics)

if __name__ == "__main__":
    main()