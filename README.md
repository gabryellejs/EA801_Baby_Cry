# Baby Cry Detection

Este projeto implementa um detector de choro de bebê utilizando um microcontrolador com um microfone, um buzzer e um display OLED. Quando um choro é detectado, o sistema toca uma melodia de ninar para acalmar o bebê.

## 📌 Funcionalidades
- Monitora o som ambiente em tempo real.
- Detecta padrões de som característicos de choro de bebê.
- Exibe informações sobre o estado do monitoramento no display OLED.
- Toca uma música de ninar ao detectar choro.
- Possui um botão para interromper a reprodução da música.

## 🛠️ Hardware Necessário
- Microcontrolador compatível com MicroPython (ex: ESP32, Raspberry Pi Pico, etc.)
- Módulo Microfone (ex: MAX9814, KY-038)
- Display OLED SSD1306 (I2C)
- Buzzer piezoelétrico
- Botão para interrupção
- Fios e protoboard para conexões

## 🔧 Instalação e Configuração
1. Instale o firmware MicroPython no seu microcontrolador.
2. Carregue os arquivos do projeto para o dispositivo usando um IDE como Thonny ou uPyCraft.
3. Conecte os componentes de acordo com os pinos configurados no código.
4. Execute o script principal no microcontrolador.

## 📜 Como Funciona
1. O microfone capta os sons do ambiente e armazena as últimas 100 leituras.
2. O sistema calcula a média e a variação do volume.
3. Se os valores ultrapassarem um limite predefinido, o choro é detectado.
4. O display OLED exibe mensagens de status.
5. Se um choro for identificado, o buzzer toca uma melodia de ninar.
6. O botão pode ser usado para interromper a música a qualquer momento.

## 📂 Estrutura do Código
- `main.py`: Código principal contendo a lógica de detecção e resposta ao choro.
- `ssd1306.py`: Biblioteca para controle do display OLED.

## 🚀 Futuras Melhorias
- Ajuste dinâmico dos limites de detecção com aprendizado de máquina.
- Implementação de um modo silencioso que apenas notifica os pais via Wi-Fi ou Bluetooth.
- Gravação de áudio e do histórico de eventos para análise posterior.

## 📜 Licença
Este projeto é de código aberto e pode ser usado livremente para fins educacionais e pessoais.

