import time as t
from collections import deque

class processMemGerenciador:
    def __init__(self, pe):
        self.PiD = pe.PiD
        self.listaSqAcesso = pe.listaSqAcesso
        self.localMem = deque()  # memoria local como fila FIFO
        self.maxLocalMem = pe.qntMem
        self.contador = 0  # index da proxima pagina que vai ser acessada
        self.numTrocas = 0
        self.politicaMem = None

    def mainCall(self):
        if self.politicaMem == 'local':
            pagina = self.listaSqAcesso[self.contador]

            if pagina in self.localMem:
                # pagina esta na memoria, nao precisa trocar
                pass
            else:
                if len(self.localMem) >= self.maxLocalMem:
                    self.localMem.popleft()  # remove a mais antiga
                    self.localMem.append(pagina)
                    self.numTrocas += 1
                else:
                    self.localMem.append(pagina)  # adiciona sem troca

            self.contador += 1  # avança no acesso da sequencia


class FIFO:
    def __init__(self, gerenciador):
        self.gerenciador = gerenciador
        self.processos = gerenciador.processos
        self.processosProntos = []
        self.sleepTime = 0.003
        self.dictProcessMem = {}

    def iniciar(self):
        print("FIFO comecou")
        self._alternanciaCirc()
        print("FIFO terminou")
        totalTrocas = sum(i.numTrocas for i in self.dictProcessMem.values())
        return totalTrocas

    def _alternanciaCirc(self):
        tamanhoInicial = len(self.processos)
        processosExecutaveis = []
        clockTick = 0

        while len(self.processosProntos) < tamanhoInicial:
            print("Tick..", clockTick, "Tack..")
            self.gerenciador.clock += 1

            if clockTick == self.gerenciador.fracaoCPU:
                print(f"\u274C Processo {processosExecutaveis[0].PiD} saiu da CPU...\n")
                t.sleep(self.sleepTime)
                processosExecutaveis.append(processosExecutaveis[0])
                processosExecutaveis.pop(0)
                clockTick = 0

            
            for i in range(0, len(self.processos)): #verifica processos que devem iniciar
                if self.processos[i].startTime <= self.gerenciador.clock:
                    print("Processo: ", self.processos[i].PiD, " iniciado...\n")
                    processosExecutaveis.append(self.processos[i])
                    pid = self.processos[i].PiD
                    if pid not in self.dictProcessMem:
                        processoMem = processMemGerenciador(self.processos[i])
                        processoMem.politicaMem = self.gerenciador.politicaMem
                        processoMem.maxLocalMem = int((processoMem.maxLocalMem // self.gerenciador.memoria.sizeMold)* self.gerenciador.percent)
                        self.dictProcessMem[pid] = processoMem

            
            for i in reversed(range(len(self.processos))):  #remove os que já foram iniciados da fila de espera
                if self.processos[i] in processosExecutaveis:
                    self.processos.pop(i)

            
            if processosExecutaveis:    # executa o processo no topo da fila circular
                proc = processosExecutaveis[0]
                proc.execTime -= 1
                self.dictProcessMem[proc.PiD].mainCall()

                if proc.execTime == 0:  #verifica se o tempo do processo terminou e tira ele da fila em caso positivo
                    print(f"\u2705 Processo {proc.PiD} terminou\n")
                    t.sleep(self.sleepTime)
                    self.processosProntos.append(proc)
                    processosExecutaveis.pop(0)

            clockTick += 1
