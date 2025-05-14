
from machine import UART, Pin
import time

class BluetoothInterface:
    def __init__(self):
        self.bt = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))
        print("Bluetooth HC-06 conectado")
    
    def send(self, message):
        try:
            self.bt.write(message + "\n")
        except Exception as e:
            print(f"Erro ao enviar via Bluetooth: {e}")
    
    def receive(self):
        if self.bt.any():
            try:
                data = self.bt.readline().decode('utf-8').strip()
                return data
            except Exception as e:
                print(f"Erro ao ler via Bluetooth: {e}")
        return None
