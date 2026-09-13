import alternanciaCirc
import FIFO #First in First out
import os 
import time as t


class Dispositivo:
    def __init__(self, id, quant_usos_simultaneos, tempo_op):
        self.id = id
        self.usos_simul = quant_usos_simultaneos
        self.tempo_op = tempo_op


class Processos:
    def __init__(self, PID, tempo_execucao, prioridade, qtd_memoria, seq_acessos, chance_req):
        self.pid = PID
        self.tempo_exec = tempo_execucao
        self.prioridade = prioridade
        self.qtd_mem = qtd_memoria
        self.seq_acessos = []
        self.chance_req = chance_req

class Gerenciador_E_S:
    def __init__(self):
        self.arquivo = "entrada_ES.txt"
        self.dispositivos_conectados = []
        self.processos = []
        self.tamanho_mem = None
        self.fracao_cpu = None
        self.politica_mem = None
        self.tamanho_paginas = None
        self.percentual_aloc = None
        
    def iniciar(self):
        self._leitor_entrada()


    def _leitor_entrada(self):
        with open(os.path.join(os.path.dirname(__file__), self.arquivo), 'r') as starter:

            linhas_limpas = []
            for line in starter.readlines():
                linhas_limpas.append(line.strip())

            #formato da entrada: algoritmoDeEscalonamento|fraçãoDeCPU|políticaMemória|tamanhoMemória|tamanhoPáginasMolduras|percentualAlocação|numDispositivosES
            #idDispositivo|numUsosSimultaneos|tempoOperação

            header = linhas_limpas[0].split("|")
            self.fracao_cpu = header[1]
            self.politica_mem = header[2]
            self.tamanho_mem = header[3]
            self.tamanho_paginas = header[4]
            self.percentual_aloc = header[5]

            for quant in int(header[6]):
                dispositivo = (linhas_limpas[quant.strip()]).split("|")
                self.dispositivos_conectados.append(Dispositivo(dispositivo[0], dispositivo[1],dispositivo[2]))

            for processos in range(len(self.dispositivos_conectados)+1, len(linhas_limpas)):
                processo = processos.split("|")
                self.processos.append(Processos(processo[1],processo[2], processo[3],processo[4],processo[5],processo[6]))


    def _exec_algoritmo(self):
        pass



            

