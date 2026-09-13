from collections import deque

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
        """Adiciona processo ao dispositivo ou à fila de espera."""
        if self.esta_disponivel():
            self.processos_em_uso.append(processo)
            return True
        else:
            self.fila_espera.append(processo)
            return False
    
    def remover_processo(self, processo):
        """Remove processo do dispositivo e promove o próximo da fila."""
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
        
        # Estado do processo
        self.estado = 'pronto'
        self.dispositivo_es = None
        
        # Métricas de tempo
        self.tempo_pronto = 0
        self.tempo_bloqueado = 0
        self.tempo_executando = 0
        
        # Controle de execução
        self.instante_inicio_cpu = None
        self.instante_conclusao = None
        self.tempo_restante_es = 0


class processMemGerenciador:
    """Gerenciador de memória local para um processo específico."""
    
    def __init__(self, processo):
        self.pid = processo.pid
        self.lista_seq_acesso = processo.seq_acesso_paginas
        self.local_mem = deque()
        self.max_local_mem = processo.qtd_memoria
        self.contador = 0
        self.num_trocas = 0
        self.politica_mem = None

    def main_call(self):
        """Processa o próximo acesso à memória do processo."""
        if self.politica_mem == 'local':
            if self.contador < len(self.lista_seq_acesso):
                pagina = self.lista_seq_acesso[self.contador]

                if pagina in self.local_mem:
                    # Página já está na memória (hit)
                    pass
                else:
                    # Page fault
                    if len(self.local_mem) >= self.max_local_mem:
                        # Memória cheia, substitui a página mais antiga (FIFO)
                        self.local_mem.popleft()
                        self.local_mem.append(pagina)
                        self.num_trocas += 1
                    else:
                        # Ainda há espaço na memória
                        self.local_mem.append(pagina)

                self.contador += 1
