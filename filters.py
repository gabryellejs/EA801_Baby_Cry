import numpy as np

# 400 - 6000 Hz
# FILTER_A = [1.0, 1.1520286221051745, 0.4239856889474127]
# FILTER_B = [0.28800715552629363, 0.0, -0.28800715552629363]

# 2500 - 6000 Hz
# FILTER_A = [1.0, 1.316143483197224, 0.341928258401388]
# FILTER_B = [0.329035870799306, 0.0, -0.329035870799306]

# 4500 - 6000 Hz
# FILTER_A = [1.0, 0.8695831964878592, 0.5652084017560705]
# FILTER_B = [0.2173957991219648, 0.0, -0.2173957991219648]

def apply_iir_bandpass_filter(data, a, b):
    """
    Apply IIR bandpass filter using NumPy and difference equation.
    """
    data = np.asarray(data, dtype=np.float32)
    filtered = np.zeros_like(data)

    x1 = x2 = y1 = y2 = 0.0
    for i in range(len(data)):
        x0 = data[i]
        y0 = (b[0] * x0 +
              b[1] * x1 +
              b[2] * x2 -
              a[1] * y1 -
              a[2] * y2)
        filtered[i] = y0
        x2, x1 = x1, x0
        y2, y1 = y1, y0
    return filtered

def apply_iir_bandpass_filter_optimized(data, a, b):
    """
    Optimized in-place IIR filter with NumPy.
    """
    data = np.asarray(data, dtype=np.float32).copy()  # Prevent modifying input
    x1 = x2 = y1 = y2 = 0.0
    b0, b1, b2 = b
    a1, a2 = a[1], a[2]
    
    for i in range(len(data)):
        x0 = data[i]
        y0 = b0 * x0 + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
        data[i] = y0
        x2, x1 = x1, x0
        y2, y1 = y1, y0
    return data

def apply_df2_bandpass_filter(data, a, b):
    """
    Direct Form II implementation using NumPy.
    """
    data = np.asarray(data, dtype=np.float32).copy()
    w1 = w2 = 0.0
    b0, b1, b2 = b
    a1, a2 = a[1], a[2]

    for i in range(len(data)):
        x0 = data[i]
        w0 = x0 - a1 * w1 - a2 * w2
        y0 = b0 * w0 + b1 * w1 + b2 * w2
        data[i] = y0
        w2, w1 = w1, w0
    return data

def apply_block_iir_filter(data, a, b, block_size=32):
    """
    Block-wise IIR filter using NumPy.
    """
    data = np.asarray(data, dtype=np.float32).copy()
    x1 = x2 = y1 = y2 = 0.0
    b0, b1, b2 = b
    a1, a2 = a[1], a[2]

    for start in range(0, len(data), block_size):
        end = min(start + block_size, len(data))
        for i in range(start, end):
            x0 = data[i]
            y0 = b0 * x0 + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
            data[i] = y0
            x2, x1 = x1, x0
            y2, y1 = y1, y0
    return data

def apply_fixedpoint_iir_filter(data, a, b):
    """
    IIR filter using a state buffer (not actual fixed-point).
    """
    data = np.asarray(data, dtype=np.float32).copy()
    state = [0.0, 0.0, 0.0, 0.0]  # x1, x2, y1, y2
    b0, b1, b2 = b
    a1, a2 = a[1], a[2]

    for i in range(len(data)):
        x0 = data[i]
        y0 = b0 * x0 + b1 * state[0] + b2 * state[1] - a1 * state[2] - a2 * state[3]
        data[i] = y0
        state[1] = state[0]
        state[0] = x0
        state[3] = state[2]
        state[2] = y0
    return data
