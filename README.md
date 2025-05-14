# Baby Cry Detection

Este projeto implementa um detector de choro de bebê utilizando um microcontrolador com um microfone, um buzzer e um display OLED. Quando um choro é detectado, o sistema toca uma melodia de ninar para tranquilizar o bebê.

## 📌 Funcionalidades
- Monitora o som ambiente em tempo real.
- Detecta padrões de som característicos de choro de bebê.
- Exibe informações sobre o estado do monitoramento no display OLED.
- Toca uma música de ninar ao detectar choro.
- Possui um botão para interromper a reprodução da música.

## 🛠️ Hardware Necessário
- Placa de desenvolvimento [BitDogLab](https://github.com/BitDogLab/BitDogLab)

![Componentes](diagrams/app_components.svg)

## 🔧 Instalação e Configuração
1. Instale o firmware MicroPython no seu microcontrolador.
2. Carregue os arquivos do projeto para o dispositivo usando um IDE como Thonny ou uPyCraft.
3. Conecte os componentes de acordo com os pinos configurados no código.
4. Execute o script principal no microcontrolador.

## 📜 Como Funciona

![Fluxograma](diagrams/app_flowchart.svg)

1. O microfone capta amostras de áudio de 2 segundos utilizando a funcionalidade de Direct Memory Access (DMA) para o conversor analógico digital (ADC) do microfone.
2. Cada amostra de áudio passa por um filtro passa faixa que seleciona apenas as frequências relativas ao choro de um bebê.
3. A energia do sinal filtrado é calculada e comparada com um threshold definido manualmente classificando se há choro ou não.
4. O display OLED exibe mensagens de status.
5. Se um choro for identificado, o buzzer toca uma melodia de ninar.
6. O botão pode ser usado para interromper a música a qualquer momento.

## 📂 Estrutura do Código
O projeto inclui tanto a base de código utilizada para a análise de sinais de áudio gravados com o hardware e desenvolvimento dos algorítmos de filtragem, como a base de códigos que deve rodar no microcontrolador (pasta `/mcu`).

- `convert_binary.py`: Este arquivo deve ser utilizado para converter os arquivos de áudio binários `.bin` que são gravados com o hardware em arquivos `.mp3` e `.csv`.
- `filter.py`: Este script implementa uma série de filtros que foram testados perante capacidade de identificação e complexidade espacial a fim de definir qual seria implementado no hardware.
- `identify.py`: Este script executa o processo de filtragem e identificação para todos os arquivos de audio convertidos por `convert_binary.py` e com base na categoria (`ground truth`) atribuida a cada audio calcula a performance do algorítmo de filtragem e gera um relatório (`evaluation_results.csv`).
- `data_analysis.ipynb`: Neste notebook os arquivos de audio gravados pelo hardware podem ser análisados, os arquivos de audio referência para determiando das frequências de corte do filtro podem ser analisados e o relatório de resultados da identificação pode ser analisado.
- `/mcu`
    - `main.py`: Código principal contendo a lógica de detecção e resposta ao choro.
    - `config.py`: Configurações para o funcionamento da aplicação no hardware.
    - `record.py`: Código que deve ser utilizado para fazer gravações de audio e salvá-las internamente no armazenamento do MCU para serem baixados e analisádos depois.
    - `/src`: Módulos exclusivos de cada functionalidade envocada em `main.py`
        - `/libs`: Bibliotecas relacionadas a periféricos anexos ao MCU

## 🚀 Futuras Melhorias
- Ajuste dinâmico dos limites de detecção com um período de calibração.
- Implementação de um modo silencioso que apenas notifica os pais via Wi-Fi ou Bluetooth.
- Gravação de áudio e do histórico de eventos para análise posterior.

## 📜 Licença
Este projeto é de código aberto e pode ser usado livremente para fins educacionais e pessoais.

