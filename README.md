# Simulador de Escalonamento de Processos com Gerenciamento de E/S

## Descrição

Este projeto implementa um simulador de sistema operacional que gerencia:
- **Escalonamento de processos** na CPU (algoritmo Round-Robin/Alternância Circular)
- **Gerenciamento de memória** com política de substituição de páginas
- **Operações de Entrada/Saída (E/S)** com múltiplos dispositivos

## Funcionalidades

### Gerenciador de E/S
- Suporte a múltiplos dispositivos de E/S
- Cada dispositivo possui capacidade limitada de processos simultâneos
- Filas de espera para dispositivos ocupados
- Processos bloqueados durante operações de E/S não podem ser escalonados para CPU

### Estados dos Processos
- **Pronto**: Aguardando para receber CPU
- **Executando**: Em execução na CPU
- **Bloqueado**: Aguardando conclusão de operação de E/S

### Estatísticas
Ao final da execução, o simulador exibe:
- Tempo total de cada processo (criação até conclusão)
- Tempo em estado pronto
- Tempo em estado bloqueado (E/S)
- Tempo em execução (CPU)

## Formato do Arquivo de Entrada

O arquivo `entrada_ES.txt` deve seguir o formato:

```
algoritmoDeEscalonamento|fraçãoDeCPU|políticaMemória|tamanhoMemória|tamanhoPáginasMolduras|percentualAlocação|numDispositivosES
idDispositivo|numUsosSimultaneos|tempoOperação
...
tempoCriação|PID|tempoDeExecução|prioridade|qtdeMemoria|sequênciaAcessoPaginasProcesso|chanceRequisitarES
...
```

### Exemplo de entrada_ES.txt:
```
alternancia|10|local|65536|512|50|4
device-0|1|3
device-1|2|5
device-2|2|2
device-3|1|6
0|1|20|59|4096|1 2 2 2 3 4 3 4 5 5 6 1 5 3 2 6 7 7 7 8|32
0|2|24|32|2048|1 2 2 2 3 4 3 4 4 4 2 3 2 1 3 2 1 2 2 3 4 3 2 2|12
0|3|32|32|4096|1 2 3 4 5 6 7 8 4 3 2 1 1 6 7 5 6 8 3 2 2 1 2 2 4 4 5 3 2 1 7 8|88
```

## Como Executar

### Pré-requisitos
- Python 3.6 ou superior
- Nenhum pacote externo necessário (usa apenas biblioteca padrão)

### Execução

```bash
cd /workspace
python main.py
```

### Saída

O simulador exibe:
1. Configurações iniciais do sistema
2. Estado do sistema a cada troca de contexto:
   - Processos em execução, prontos e bloqueados
   - Estado de cada dispositivo de E/S
3. Estatísticas finais de execução

## Estrutura do Projeto

```
/workspace/
├── main.py              # Implementação principal do simulador
├── alternanciaCirc.py   # Algoritmo de alternância circular (referência)
├── FIFO.py             # Algoritmo FIFO e gerenciamento de memória (referência)
├── entrada_ES.txt      # Arquivo de configuração e entrada
├── README.md           # Este arquivo
└── saida_simulacao.log # Log de saída da simulação (gerado na execução)
```

## Classes Principais

### Dispositivo
Representa um dispositivo de E/S com:
- Identificador único
- Capacidade de usos simultâneos
- Tempo de operação
- Lista de processos em uso
- Fila de espera

### Processo
Representa um processo com:
- PID, tempo de criação, tempo de execução
- Prioridade, quantidade de memória
- Sequência de acessos a páginas
- Chance de requisitar E/S
- Estado atual e tempos acumulados

### GerenciadorES
Gerencia todo o sistema:
- Carrega configuração do arquivo
- Controla escalonamento de processos
- Gerencia dispositivos de E/S
- Exibe estado do sistema
- Calcula estatísticas finais

## Autor

Simulador SO - Trabalho de Sistemas Operacionais

## Licença

Uso acadêmico
