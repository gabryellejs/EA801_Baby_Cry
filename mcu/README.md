# Baby Cry Detection System for Raspberry Pi Pico

This system detects baby crying using a microphone, processes the audio signal, and plays a melody through a buzzer when crying is detected. It also provides status updates via an OLED display and an LED indicator.

## Hardware Requirements

- Raspberry Pi Pico (or Pico W)
- Microphone module with analog output (connected to ADC)
- OLED display (SSD1306, 128x64 pixels)
- Buzzer 
- Push button (for stopping the melody)
- Status LED
- Appropriate resistors and connecting wires

## Hardware Connections

- **Microphone**: Connect to GPIO 28 (ADC channel 2)
- **OLED Display**: 
  - SDA: GPIO 14
  - SCL: GPIO 15
- **Buzzer**: GPIO 21
- **Button**: GPIO 5 (with pull-up)
- **Status LED**: GPIO 25

## Software Structure

The system is organized into the following modules:

- **main.py**: Entry point and orchestrator for the system
- **config.py**: Centralized configuration parameters and constants
- **cry_detector.py**: Handles microphone sampling and cry detection
- **audio_processing.py**: Signal processing functions for filtering and analysis
- **display_manager.py**: Manages the OLED display
- **buzzer_control.py**: Controls the buzzer for playing melodies

## Installation

1. Install MicroPython on your Raspberry Pi Pico if not already installed.
2. Copy all Python files to the Pico's file system.
3. Make sure to install the required SSD1306 library for the OLED display (`ssd1306.py`).

## Configuration Options

You can modify various parameters in the `config.py` file:

- **Sampling parameters**: Adjust frequency, duration, and interval
- **Detection threshold**: Change sensitivity of cry detection
- **Musical notes and melody**: Customize the melody played when crying is detected
- **Hardware pins**: Modify if using different GPIO connections

## How It Works

1. The system continuously samples audio from the microphone.
2. The audio signal is processed through a bandpass filter optimized for baby cry frequencies.
3. If the energy of the filtered signal exceeds a threshold, crying is detected.
4. When crying is detected:
   - The status LED blinks rapidly
   - The OLED display shows "Choro detectado!" (Crying detected)
   - The buzzer plays a melody
5. The melody can be interrupted by pressing the button.

## Extending the System

To add new features to the system:

1. Create a new module for your feature (e.g., `temperature_sensor.py`)
2. Add any necessary configuration to `config.py`
3. Initialize and use your module in `main.py`

### Example: Adding Temperature Monitoring

```python
# In temperature_sensor.py
from machine import ADC, Pin
from config import TEMP_PIN, TEMP_THRESHOLD

class TemperatureSensor:
    def __init__(self):
        self.sensor = ADC(Pin(TEMP_PIN))
        
    def read_temperature(self):
        # Read and convert temperature
        raw = self.sensor.read_u16()
        temp_c = raw * 3.3 / 65535 * 100  # Example conversion
        return temp_c
        
    def is_too_hot(self):
        return self.read_temperature() > TEMP_THRESHOLD
```

```python
# In main.py - add to imports
from temperature_sensor import TemperatureSensor

# In main() function - add initialization
temp_sensor = TemperatureSensor()

# In main loop - add temperature check
current_temp = temp_sensor.read_temperature()
if temp_sensor.is_too_hot():
    display.update("Muito quente!", f"{current_temp:.1f}C")
    buzzer.play_note("A4", 0.2)  # Alert tone
```

## Troubleshooting

- **No cry detection**: Adjust the `VOLTAGE_THRESHOLD` in `config.py` to make it more sensitive
- **False positives**: Increase the threshold to make detection less sensitive
- **Display not working**: Check I2C connections and make sure the SSD1306 library is installed
- **System crashing**: Memory issues can occur - try reducing `SAMPLES` in `config.py`

## Performance Considerations

- The system is optimized for the limited resources of the Raspberry Pi Pico.
- The Direct Form II IIR filter implementation uses minimal state variables.
- Hardcoded filter coefficients avoid complex math during operation.
- Garbage collection is performed periodically to manage memory.