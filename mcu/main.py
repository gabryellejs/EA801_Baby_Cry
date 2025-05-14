
#!/usr/bin/env python
import gc
import time
from src.cry_detector import CryDetector
from src.display_manager import DisplayManager
from src.buzzer_control import BuzzerControl
from src.led_indicator import LedIndicator
from src.bluetooth_interface import BluetoothInterface
from config import SAMPLING_INTERVAL, LED_PIN, MUSIC_VOLUME


def main():
    gc.collect()
    print("Inicializando sistema de detecção de choro...\n")

    display = DisplayManager()
    buzzer = BuzzerControl()
    detector = CryDetector()
    led = LedIndicator()
    bt = BluetoothInterface()
    
    sistema_ativo = True
    volume = MUSIC_VOLUME

    try:
        while True:
            command = bt.receive()
            if command:
                print("Comando recebido:", command)
                cmd = command.lower()

                if cmd == "ligar":
                    sistema_ativo = True
                    display.update("Sistema", "Ativado")
                    bt.send("Sistema ativado.")
                
                elif cmd == "desligar":
                    sistema_ativo = False
                    display.update("Sistema", "Desligado")
                    bt.send("Sistema desativado.")
                
                elif cmd == "parar":
                    buzzer.buzzer.duty_u16(0)
                    display.update("Música", "parada")
                    bt.send("Música parada.")

                elif cmd == "status":
                    bt.send("Ativo" if sistema_ativo else "Inativo")

                elif cmd.startswith("msg:"):
                    text = cmd[4:].strip()
                    display.update("Msg:", text)
                    bt.send(f"Mensagem mostrada: {text}")
                
                elif cmd == "leitura":
                    display.update("Forçando", "leitura...")
                    detector.sample_audio()
                    is_crying, energy = detector.detect_cry()
                    msg = f"Leitura - Choro: {'SIM' if is_crying else 'NÃO'} ({energy:.5f})"
                    display.update("Leitura", "concluída")
                    bt.send(msg)

                elif cmd.startswith("volume:"):
                    try:
                        val = int(cmd.split(":")[1])
                        if 0 <= val <= 100:
                            buzzer.set_volume(val)
                            bt.send(f"Volume ajustado para {val}%")
                        else:
                            bt.send("Valor de volume fora do intervalo (0-100).")
                    except:
                        bt.send("Erro ao interpretar volume.")
            
            if sistema_ativo:
                display.update("Monitorando", "som...")
                detector.sample_audio()
                is_crying, energy = detector.detect_cry()
                if is_crying:
                    print(f"Choro detectado! ({energy=:.5f})")
                    display.update("Choro", "detectado!")
                    led.blink(duration_ms=100, times=5)
                    # buzzer.play_melody()
                    bt.send(f"Choro detectado! Energia: {energy:.5f}")
                else:
                    print(f"Sem choro ({energy:.5f})")
                time.sleep(SAMPLING_INTERVAL)

    except KeyboardInterrupt:
        print("\nEncerrado pelo usuário.")
        detector.cleanup()

if __name__ == "__main__":
    main()
