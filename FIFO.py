"""
Módulo FIFO - Algoritmo First-In-First-Out com Gerenciamento de E/S
=====================================================================
Implementa o escalonamento FIFO com suporte a operações de E/S,
estados de processo e estatísticas detalhadas.
"""

import time as t
import random
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


class processMemGerenciador:
    """Gerenciador de memória para processos usando política FIFO."""
    
    def __init__(self, pe):
        self.PiD = pe.pid
        self.listaSqAcesso = pe.seq_acesso_paginas
        self.localMem = deque()
        self.maxLocalMem = pe.qtd_memoria
        self.contador = 0
        self.numTrocas = 0
        self.politicaMem = None

    def mainCall(self):
        if self.politicaMem == 'local':
            if self.contador < len(self.listaSqAcesso):
                pagina = self.listaSqAcesso[self.contador]

                if pagina in self.localMem:
                    pass
                else:
                    if len(self.localMem) >= self.maxLocalMem:
                        self.localMem.popleft()
                        self.localMem.append(pagina)
                        self.numTrocas += 1
                    else:
                        self.localMem.append(pagina)

                self.contador += 1


class FIFO:
    """
    Implementa o algoritmo de escalonamento FIFO com gerenciamento de E/S.
    """
    
    def __init__(self, gerenciador):
        self.gerenciador = gerenciador
        self.todos_processos = gerenciador.todos_processos
        self.processos_prontos = []
        self.processos_executando = []
        self.processos_bloqueados = []
        self.sleepTime = 0.003
        self.dictProcessMem = {}
        self.dispositivos = gerenciador.dispositivos
        self.operacoes_es_ativas = {}
        self.fracao_cpu = gerenciador.fracao_cpu

    def iniciar(self):
        """Inicia a execução do escalonador FIFO."""
        print("FIFO comecou")
        self._executar()
        print("FIFO terminou")
        totalTrocas = sum(i.numTrocas for i in self.dictProcessMem.values())
        return totalTrocas

    def exibir_estado_sistema(self):
        """Exibe o estado atual de processos e dispositivos."""
        print("\n" + "=" * 80)
        print(f"CLOCK DO SISTEMA: {self.gerenciador.clock}")
        print("=" * 80)
        
        print("\n📊 ESTADO DOS PROCESSOS:")
        print("-" * 80)
        
        print("🔴 EM EXECUÇÃO:")
        if self.processos_executando:
            for proc in self.processos_executando:
                print(f"   PID {proc.pid:3d} | Tempo restante CPU: {proc.tempo_execucao_restante:3d}")
        else:
            print("   Nenhum processo em execução")
        
        print("\n🟢 PRONTOS:")
        if self.processos_prontos:
            for proc in self.processos_prontos:
                print(f"   PID {proc.pid:3d} | Tempo restante CPU: {proc.tempo_execucao_restante:3d}")
        else:
            print("   Nenhum processo pronto")
        
        print("\n🟡 BLOQUEADOS (E/S):")
        if self.processos_bloqueados:
            for proc in self.processos_bloqueados:
                if proc.dispositivo_es:
                    disp_info = f"Dispositivo: {proc.dispositivo_es.id}"
                else:
                    disp_info = "Aguardando dispositivo"
                print(f"   PID {proc.pid:3d} | Tempo restante CPU: {proc.tempo_execucao_restante:3d} | {disp_info}")
        else:
            print("   Nenhum processo bloqueado")
        
        print("\n💾 ESTADO DOS DISPOSITIVOS DE E/S:")
        print("-" * 80)
        for disp_id, disp in sorted(self.dispositivos.items()):
            print(f"\n  Dispositivo {disp.id}:")
            print(f"    Capacidade: {disp.usos_simultaneos} processo(s) simultâneo(s)")
            print(f"    Tempo de operação: {disp.tempo_operacao} unidades")
            
            if disp.processos_em_uso:
                pids_em_uso = [p.pid for p in disp.processos_em_uso]
                print(f"    Em uso por: PIDs {pids_em_uso}")
            else:
                print(f"    Em uso por: Nenhum")
            
            if disp.fila_espera:
                pids_fila = [p.pid for p in disp.fila_espera]
                print(f"    Fila de espera: PIDs {pids_fila}")
            else:
                print(f"    Fila de espera: Vazia")
        
        print("\n" + "=" * 80)

    def verificar_requisicao_es(self, processo):
        """Determina probabilisticamente se o processo requisita E/S."""
        if random.random() < processo.chance_req_es:
            dispositivos_lista = list(self.dispositivos.values())
            dispositivo_escolhido = random.choice(dispositivos_lista)
            momento_req = random.randint(0, self.fracao_cpu - 1)
            return dispositivo_escolhido, momento_req
        return None, -1

    def solicitar_es(self, processo, dispositivo):
        """Processo solicita operação de E/S em um dispositivo."""
        print(f"\n⏸️  Processo {processo.pid} solicitou E/S no dispositivo {dispositivo.id}")
        
        if processo in self.processos_executando:
            self.processos_executando.remove(processo)
        
        processo.estado = 'bloqueado'
        processo.dispositivo_es = dispositivo
        processo.tempo_restante_es = dispositivo.tempo_operacao
        
        sucesso = dispositivo.adicionar_processo(processo)
        
        if sucesso:
            print(f"   → Processo {processo.pid} iniciou E/S (duração: {dispositivo.tempo_operacao})")
            self.operacoes_es_ativas[processo.pid] = {
                'dispositivo': dispositivo,
                'tempo_restante': dispositivo.tempo_operacao
            }
        else:
            print(f"   → Processo {processo.pid} entrou na fila de espera")
        
        if processo not in self.processos_bloqueados:
            self.processos_bloqueados.append(processo)

    def processar_operacoes_es(self):
        """Avança as operações de E/S e desbloqueia processos completos."""
        processos_para_desbloquear = []
        
        for pid, operacao in list(self.operacoes_es_ativas.items()):
            operacao['tempo_restante'] -= 1
            
            if operacao['tempo_restante'] <= 0:
                processo = None
                for p in self.processos_bloqueados:
                    if p.pid == pid:
                        processo = p
                        break
                
                if processo:
                    processos_para_desbloquear.append(processo)
                
                dispositivo = operacao['dispositivo']
                processo_promovido = dispositivo.remover_processo(processo)
                
                del self.operacoes_es_ativas[pid]
                
                if processo_promovido:
                    self.operacoes_es_ativas[processo_promovido.pid] = {
                        'dispositivo': dispositivo,
                        'tempo_restante': dispositivo.tempo_operacao
                    }
                    print(f"   → Processo {processo_promovido.pid} iniciou E/S (da fila de espera)")
        
        for processo in processos_para_desbloquear:
            self.completar_es(processo)

    def completar_es(self, processo):
        """Completa operação de E/S e move processo para prontos."""
        print(f"✅ Processo {processo.pid} completou E/S")
        
        dispositivo = processo.dispositivo_es
        processo.estado = 'pronto'
        processo.dispositivo_es = None
        processo.tempo_restante_es = 0
        
        if processo in self.processos_bloqueados:
            self.processos_bloqueados.remove(processo)
        
        if processo not in self.processos_prontos:
            self.processos_prontos.append(processo)

    def atualizar_tempos_espera(self):
        """Atualiza contadores de tempo de espera dos processos."""
        for proc in self.processos_prontos:
            proc.tempo_pronto += 1
        
        for proc in self.processos_bloqueados:
            proc.tempo_bloqueado += 1

    def exibir_estatisticas_finais(self):
        """Exibe estatísticas finais de execução de todos os processos."""
        print("\n" + "=" * 80)
        print("📈 ESTATÍSTICAS FINAIS DE EXECUÇÃO")
        print("=" * 80)
        
        for processo in sorted(self.todos_processos, key=lambda p: p.pid):
            tempo_total = processo.instante_conclusao - processo.tempo_criacao if processo.instante_conclusao else 0
            
            print(f"\nProcesso PID {processo.pid}:")
            print(f"   Tempo total (criacao -> conclusao): {tempo_total:3d} unidades")
            print(f"   Tempo em estado pronto:            {processo.tempo_pronto:3d} unidades")
            print(f"   Tempo em estado bloqueado (E/S):   {processo.tempo_bloqueado:3d} unidades")
            print(f"   Tempo em execucao (CPU):           {processo.tempo_executando:3d} unidades")
        
        print("\n" + "=" * 80)

    def _executar(self):
        """Executa o escalonador FIFO com gerenciamento de E/S."""
        processos_aguardando = self.todos_processos.copy()
        fila_fifo = []
        
        while (processos_aguardando or self.processos_prontos or 
               self.processos_executando or self.processos_bloqueados or fila_fifo):
            
            processos_chegaram = [p for p in processos_aguardando 
                                  if p.tempo_criacao <= self.gerenciador.clock]
            for p in processos_chegaram:
                print(f"\n📥 Clock {self.gerenciador.clock}: Processo {p.pid} chegou ao sistema")
                processos_aguardando.remove(p)
                self.processos_prontos.append(p)
            
            if self.operacoes_es_ativas:
                print(f"\n⏱️  Processando operacoes de E/S...")
                self.processar_operacoes_es()
            
            while self.processos_prontos:
                proc = self.processos_prontos.pop(0)
                if proc not in fila_fifo:
                    fila_fifo.append(proc)
            
            if not self.processos_executando and fila_fifo:
                proximo = fila_fifo.pop(0)
                if proximo.estado != 'bloqueado':
                    proximo.estado = 'executando'
                    self.processos_executando.append(proximo)
                    proximo.instante_inicio_cpu = self.gerenciador.clock
                    print(f"\n⬆️  Clock {self.gerenciador.clock}: Processo {proximo.pid} recebeu a CPU")
            
            self.exibir_estado_sistema()
            
            if self.processos_executando:
                proc_atual = self.processos_executando[0]
                tempo_fatia = min(proc_atual.tempo_execucao_restante, self.fracao_cpu)
                
                disp_es, momento_req = self.verificar_requisicao_es(proc_atual)
                
                if disp_es and momento_req >= 0 and momento_req < tempo_fatia:
                    print(f"\n⏱️  Processo {proc_atual.pid} executou por {momento_req} unidades")
                    proc_atual.tempo_execucao_restante -= momento_req
                    proc_atual.tempo_executando += momento_req
                    self.gerenciador.clock += momento_req
                    
                    self.solicitar_es(proc_atual, disp_es)
                else:
                    print(f"\n▶️  Processo {proc_atual.pid} executando por {tempo_fatia} unidades")
                    proc_atual.tempo_execucao_restante -= tempo_fatia
                    proc_atual.tempo_executando += tempo_fatia
                    self.gerenciador.clock += tempo_fatia
                    
                    if proc_atual.tempo_execucao_restante <= 0:
                        proc_atual.instante_conclusao = self.gerenciador.clock
                        print(f"\n✅ Clock {self.gerenciador.clock}: Processo {proc_atual.pid} TERMINOU")
                        self.processos_executando.remove(proc_atual)
                        
                        if proc_atual.pid in self.dictProcessMem:
                            self.dictProcessMem[proc_atual.pid].mainCall()
                    else:
                        proc_atual.estado = 'pronto'
                        self.processos_executando.remove(proc_atual)
                        fila_fifo.append(proc_atual)
                        print(f"\n⏹️  Clock {self.gerenciador.clock}: Processo {proc_atual.pid} saiu da CPU")
            
            self.atualizar_tempos_espera()
            t.sleep(0.05)
        
        self.exibir_estatisticas_finais()
