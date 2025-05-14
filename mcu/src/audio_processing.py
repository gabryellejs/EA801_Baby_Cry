#!/usr/bin/env python
"""
Audio Processing Module
----------------------
Provides functions for digital signal processing
focused on baby cry detection.
"""

import array
from config import FILTER_A, FILTER_B

def apply_bandpass_filter(data):
    """
    Apply Direct Form II IIR bandpass filter to audio data.
    Uses only 2 state variables for efficiency.
    
    Args:
        data: Array of audio samples
        
    Returns:
        Array of filtered audio samples
    """
    filtered = array.array('f', data) if isinstance(data, array.array) else array.array('f', data)
    
    # Direct Form II uses only two state variables
    w1 = w2 = 0.0
    
    # Pre-fetch coefficients
    b0, b1, b2 = FILTER_B[0], FILTER_B[1], FILTER_B[2]
    a1, a2 = FILTER_A[1], FILTER_A[2]
    
    # Apply filter to each sample
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
    """
    Calculate energy of filtered audio signal.
    
    Args:
        filtered_data: Array of filtered audio samples
        
    Returns:
        Energy value (squared sum normalized by length)
    """
    energy = 0
    for sample in filtered_data:
        energy += sample * sample
    
    # Normalize by signal length
    if len(filtered_data) > 0:
        energy /= len(filtered_data)
    
    return energy