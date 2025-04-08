from machine import Pin, PWM, ADC, SoftI2C
import ssd1306  # Biblioteca para o display OLED
import time

# Configuração do buzzer, botão e microfone
buzzer = PWM(Pin(21))  # Buzzer no GPIO21
botao = Pin(5, Pin.IN, Pin.PULL_UP)  # Botão no GPIO5 (com pull-up interno)
microfone = ADC(Pin(28))  # Microfone no GPIO28 (entrada analógica)

# Configuração do Display OLED (SSD1306, I2C nos pinos GPIO 15 e 14)
i2c_oled = SoftI2C(scl=Pin(15), sda=Pin(14))
oled = ssd1306.SSD1306_I2C(128, 64, i2c_oled)

# Notas musicais e suas frequências em Hz
NOTAS = {
    "C4": 262, "D4": 294, "E4": 330, "F4": 349, "G4": 392,
    "A4": 440, "B4": 494, "C5": 523
}

# Melodia de "Se essa rua fosse minha"
MUSICA = [
    ("C4", 0.5), ("D4", 0.5), ("E4", 0.5), ("F4", 0.5), ("G4", 0.5), ("G4", 0.5), ("A4", 0.5), ("G4", 1.0),
    ("G4", 0.5), ("F4", 0.5), ("E4", 0.5), ("D4", 0.5), ("E4", 0.5), ("F4", 0.5), ("G4", 1.0),
    ("C4", 0.5), ("D4", 0.5), ("E4", 0.5), ("F4", 0.5), ("G4", 0.5), ("G4", 0.5), ("A4", 0.5), ("G4", 1.0),
    ("G4", 0.5), ("F4", 0.5), ("E4", 0.5), ("D4", 0.5), ("C4", 0.5), ("C4", 1.0)
]

# Buffer circular para armazenar as últimas 100 medições
buffer_som = [0] * 100


def atualizar_display(linha1="", linha2=""):
    """Exibe duas linhas de texto no display OLED"""
    oled.fill(0)  # Limpa a tela
    oled.text(linha1, 0, 20)  # Primeira linha
    oled.text(linha2, 0, 35)  # Segunda linha
    oled.show()


def tocar_nota(nota, duracao):
    """Toca uma nota pelo tempo especificado e verifica o botão"""
    if nota in NOTAS:
        buzzer.freq(NOTAS[nota])  # Define a frequência da nota
        buzzer.duty_u16(1000)  # Define o volume
        inicio = time.ticks_ms()  # Marca o tempo inicial

        while time.ticks_diff(time.ticks_ms(), inicio) < duracao * 1000:
            if botao.value() == 0:  # Se o botão for pressionado, para a música
                buzzer.duty_u16(0)
                atualizar_display("Musica", "interrompida")
                return False
        buzzer.duty_u16(0)  # Silencia o buzzer entre as notas
        time.sleep(0.1)  # Pequena pausa entre as notas
    return True


def tocar_musica():
    """Executa a música completa, parando se o botão for pressionado"""
    atualizar_display("Tocando", "musica...")
    for nota, duracao in MUSICA:
        if not tocar_nota(nota, duracao):
            break  # Sai do loop se o botão for pressionado


def detectar_choro():
    """Atualiza o buffer de som e detecta sons altos e irregulares (possível choro) em tempo real"""
    global buffer_som
    
    # Adiciona nova leitura e remove a mais antiga
    nova_leitura = microfone.read_u16()
    buffer_som.pop(0)
    buffer_som.append(nova_leitura)
    
    # Cálculo do volume médio e variação
    media = sum(buffer_som) / len(buffer_som)
    pico = max(buffer_som) - min(buffer_som)
    
    print(f"Volume médio: {media}, Pico: {pico}")  # Para depuração
    
    # Definição simples para "choro": volume alto e variação grande
    if media > 30000 and pico > 15000:
        atualizar_display("Choro", "detectado!")
        tocar_musica()
    else:
        atualizar_display("Monitorando", "som...")


# Loop principal: monitora o som continuamente
while True:
    detectar_choro()
    time.sleep(1)  # Aguarda 1 segundo antes da próxima atualização
