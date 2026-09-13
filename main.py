"""
Simulador de Escalonamento de Processos com Gerenciamento de E/S
================================================================
Este módulo implementa um simulador de sistema operacional que gerencia
processos, escalonamento de CPU e operações de Entrada/Saída (E/S).

Suporta os algoritmos:
- FIFO (First-In-First-Out)
- Round-Robin (Alternância Circular)

Autor: Simulador SO
Versão: 1.0
"""

import os
import sys
import time as t
import random

# Importa os algoritmos de escalonamento dos módulos externos
from FIFO import FIFO
from alternanciaCirc import AlternanciaCirc


class Dispositivo:
    """Representa um dispositivo de E/S no sistema."""
    
    def __init__(self, id_dispositivo, num_usos_simultaneos, tempo_operacao):
        self.id = id_dispositivo
        self.usos_simultaneos = int(num_usos_simultaneos)
        self.tempo_operacao = int(tempo_operacao)
        self.processos_em_uso = []
        self.fila_espera = []
    
    def esta_disponivel(self):
        """Verifica se há slots disponíveis no dispositivo."""
        return len(self.processos_em_uso) < self.usos_simultaneos
    
    def adicionar_processo(self, processo):
        """Adiciona um processo ao dispositivo ou à fila de espera."""
        if self.esta_disponivel():
            self.processos_em_uso.append(processo)
            return True
        else:
            self.fila_espera.append(processo)
            return False
    
    def remover_processo(self, processo):
        """Remove um processo do dispositivo e promove o próximo da fila."""
        if processo in self.processos_em_uso:
            self.processos_em_uso.remove(processo)
            if self.fila_espera and self.esta_disponivel():
                proximo = self.fila_espera.pop(0)
                self.processos_em_uso.append(proximo)
                return proximo
        return None


class Processo:
    """Representa um processo no sistema operacional."""
    
    def __init__(self, tempo_criacao, pid, tempo_execucao, prioridade, 
                 qtd_memoria, seq_acesso_paginas, chance_req_es):
        self.tempo_criacao = int(tempo_criacao)
        self.pid = int(pid)
        self.tempo_execucao_total = int(tempo_execucao)
        self.tempo_execucao_restante = int(tempo_execucao)
        self.prioridade = int(prioridade)
        self.qtd_memoria = int(qtd_memoria)
        self.seq_acesso_paginas = [int(x) for x in seq_acesso_paginas.split()]
        self.chance_req_es = float(chance_req_es) / 100.0
        
        self.estado = 'pronto'
        self.dispositivo_es = None
        
        self.tempo_pronto = 0
        self.tempo_bloqueado = 0
        self.tempo_executando = 0
        
        self.instante_inicio_cpu = None
        self.instante_conclusao = None
        self.tempo_restante_es = 0


class GerenciadorES:
    """
    Gerenciador principal do sistema que carrega configuração e delega
    a execução para o algoritmo de escalonamento apropriado.
    """
    
    def __init__(self):
        self.arquivo_entrada = "entrada_ES.txt"
        self.dispositivos = {}
        self.todos_processos = []
        self.processos_executando = []
        self.processos_prontos = []
        self.processos_bloqueados = []
        
        self.algoritmo_escalonamento = None
        self.fracao_cpu = 10
        self.politica_memoria = None
        self.tamanho_memoria = None
        self.tamanho_paginas_molduras = None
        self.percentual_alocacao = None
        
        self.clock = 0
        self.operacoes_es_ativas = {}
    
    def carregar_entrada(self):
        """Lê e parseia o arquivo de entrada configurando o sistema."""
        caminho_arquivo = os.path.join(os.path.dirname(__file__), self.arquivo_entrada)
        
        with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
            linhas = [linha.strip() for linha in arquivo.readlines() if linha.strip()]
        
        header = linhas[0].split("|")
        self.algoritmo_escalonamento = header[0].strip()
        self.fracao_cpu = int(header[1])
        self.politica_memoria = header[2].strip()
        self.tamanho_memoria = int(header[3])
        self.tamanho_paginas_molduras = int(header[4])
        self.percentual_alocacao = int(header[5])
        num_dispositivos = int(header[6])
        
        for i in range(1, num_dispositivos + 1):
            partes = linhas[i].split("|")
            id_disp = partes[0].strip()
            num_usos = int(partes[1])
            tempo_op = int(partes[2])
            self.dispositivos[id_disp] = Dispositivo(id_disp, num_usos, tempo_op)
        
        for i in range(num_dispositivos + 1, len(linhas)):
            partes = linhas[i].split("|")
            processo = Processo(
                tempo_criacao=int(partes[0]),
                pid=int(partes[1]),
                tempo_execucao=int(partes[2]),
                prioridade=int(partes[3]),
                qtd_memoria=int(partes[4]),
                seq_acesso_paginas=partes[5],
                chance_req_es=float(partes[6])
            )
            self.todos_processos.append(processo)
    
    def executar(self):
        """
        Executa o simulador completo delegando para o algoritmo apropriado.
        """
        self.carregar_entrada()
        
        print("=" * 80)
        print("SIMULADOR DE ESCALONAMENTO COM GERENCIAMENTO DE E/S")
        print("=" * 80)
        print(f"Algoritmo de escalonamento: {self.algoritmo_escalonamento}")
        print(f"Fracao de CPU (time slice): {self.fracao_cpu}")
        print(f"Politica de memoria:        {self.politica_memoria}")
        print(f"Tamanho da memoria:         {self.tamanho_memoria}")
        print(f"Tamanho pagina/moldura:     {self.tamanho_paginas_molduras}")
        print(f"Percentual de alocacao:     {self.percentual_alocacao}%")
        print(f"Numero de dispositivos E/S: {len(self.dispositivos)}")
        print("=" * 80)
        
        # Seleciona e executa o algoritmo de escalonamento apropriado
        if self.algoritmo_escalonamento.lower() == 'fifo':
            escalonador = FIFO(self)
            escalonador.iniciar()
        elif self.algoritmo_escalonamento.lower() in ['roundrobin', 'alternanciacircular', 'rr', 'alternancia']:
            escalonador = AlternanciaCirc(self)
            escalonador.iniciar()
        else:
            print(f"ERRO: Algoritmo '{self.algoritmo_escalonamento}' não reconhecido.")
            print("Algoritmos suportados: FIFO, RoundRobin (ou AlternanciaCircular)")
            sys.exit(1)


def main():
    """Função principal de entrada do simulador."""
    print("\n" + "=" * 80)
    print("INICIANDO SIMULADOR DE SISTEMAS OPERACIONAIS")
    print("Gerenciamento de Processos e Operacoes de E/S")
    print("=" * 80 + "\n")
    
    gerenciador = GerenciadorES()
    gerenciador.executar()
    
    print("\n" + "=" * 80)
    print("SIMULAÇÃO CONCLUÍDA COM SUCESSO")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
