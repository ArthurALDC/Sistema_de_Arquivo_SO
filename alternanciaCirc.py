import time as t
import random
from modelos import Dispositivo, Processo, processMemGerenciador

class AlternanciaCirc:
    def __init__(self, gerenciador):
        self.gerenciador = gerenciador
        self.processos_prontos = []
        self.processos_executando = []
        self.processos_bloqueados = []
        self.operacoes_es_ativas = {}
        self.dict_process_mem = {}
        self.sleep_time = 0.05
        self.fracao_cpu = gerenciador.fracao_cpu

    def iniciar(self):
        print("\n--- INICIANDO ESCALONAMENTO ROUND-ROBIN (ALTERNANCIA CIRCULAR) ---\n")
        self._executar()
        print("\n--- SIMULACAO CONCLUIDA ---")

    def exibir_estado_sistema(self):
        """Exibe o estado atual de processos e dispositivos."""
        print("\n" + "-" * 70)
        print(f"CLOCK DO SISTEMA: {self.gerenciador.clock}")
        print("-" * 70)
        
        print("PROCESSOS:")
        if self.processos_executando:
            for p in self.processos_executando:
                print(f"  [EXECUTANDO] PID {p.pid:2d} | Restante CPU: {p.tempo_execucao_restante:2d}")
        else:
            print("  [EXECUTANDO] Nenhum")
            
        for p in self.processos_prontos:
            print(f"  [PRONTO]     PID {p.pid:2d} | Restante CPU: {p.tempo_execucao_restante:2d}")
            
        for p in self.processos_bloqueados:
            disp_info = p.dispositivo_es.id if p.dispositivo_es else "Aguardando"
            print(f"  [BLOQUEADO]  PID {p.pid:2d} | Restante CPU: {p.tempo_execucao_restante:2d} | Dispositivo: {disp_info}")
        
        print("\nDISPOSITIVOS E/S:")
        for disp in sorted(self.gerenciador.dispositivos.values(), key=lambda x: x.id):
            pids_em_uso = [p.pid for p in disp.processos_em_uso]
            pids_fila = [p.pid for p in disp.fila_espera]
            print(f"  {disp.id:9s} | Uso: {len(disp.processos_em_uso)}/{disp.usos_simultaneos} | Em uso: {pids_em_uso if pids_em_uso else 'Nenhum'} | Fila: {pids_fila if pids_fila else 'Vazia'}")
        print("-" * 70)

    def verificar_requisicao_es(self, processo):
        """Determina probabilisticamente se o processo requisita E/S durante a fatia."""
        if random.random() < processo.chance_req_es:
            dispositivos_lista = list(self.gerenciador.dispositivos.values())
            dispositivo_escolhido = random.choice(dispositivos_lista)
            # O momento da requisição é sorteado dentro da fatia de CPU (quantum)
            momento_req = random.randint(0, self.fracao_cpu - 1)
            return dispositivo_escolhido, momento_req
        return None, -1

    def solicitar_es(self, processo, dispositivo):
        """Processo solicita operação de E/S em um dispositivo."""
        print(f"\n  Processo {processo.pid} solicitou E/S no dispositivo {dispositivo.id}")
        
        if processo in self.processos_executando:
            self.processos_executando.remove(processo)
        
        processo.estado = 'bloqueado'
        processo.dispositivo_es = dispositivo
        processo.tempo_restante_es = dispositivo.tempo_operacao
        
        sucesso = dispositivo.adicionar_processo(processo)
        
        if sucesso:
            print(f"     -> Processo {processo.pid} iniciou E/S (duracao: {dispositivo.tempo_operacao})")
            self.operacoes_es_ativas[processo.pid] = {
                'dispositivo': dispositivo,
                'tempo_restante': dispositivo.tempo_operacao
            }
        else:
            print(f"     -> Processo {processo.pid} entrou na fila de espera do dispositivo")
        
        if processo not in self.processos_bloqueados:
            self.processos_bloqueados.append(processo)

    def processar_operacoes_es(self):
        """Avança as operações de E/S e desbloqueia processos completos."""
        processos_para_desbloquear = []
        
        for pid, operacao in list(self.operacoes_es_ativas.items()):
            operacao['tempo_restante'] -= 1
            
            if operacao['tempo_restante'] <= 0:
                processo = next((p for p in self.processos_bloqueados if p.pid == pid), None)
                
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
                    print(f"     -> Processo {processo_promovido.pid} iniciou E/S (da fila de espera)")
        
        for processo in processos_para_desbloquear:
            self.completar_es(processo)

    def completar_es(self, processo):
        """Finaliza a E/S e retorna o processo para a fila de prontos."""
        print(f"  Processo {processo.pid} completou E/S e voltou para PRONTO")
        processo.estado = 'pronto'
        processo.dispositivo_es = None
        processo.tempo_restante_es = 0
        
        if processo in self.processos_bloqueados:
            self.processos_bloqueados.remove(processo)
        
        if processo not in self.processos_prontos:
            self.processos_prontos.append(processo)

    def atualizar_tempos_espera(self):
        """Incrementa os contadores de tempo de espera."""
        for proc in self.processos_prontos:
            proc.tempo_pronto += 1
        for proc in self.processos_bloqueados:
            proc.tempo_bloqueado += 1

    def exibir_estatisticas_finais(self):
        """Exibe o relatório final de métricas."""
        print("\n" + "=" * 80)
        print("ESTATISTICAS FINAIS DE EXECUCAO")
        print("=" * 80)
        print(f"{'PID':<5} | {'Tempo Total':<15} | {'Tempo em Pronto':<15} | {'Tempo Bloqueado':<15} | {'Tempo CPU':<10}")
        print("-" * 80)
        
        for processo in sorted(self.gerenciador.todos_processos, key=lambda p: p.pid):
            tempo_total = processo.instante_conclusao - processo.tempo_criacao if processo.instante_conclusao else 0
            print(f"{processo.pid:<5} | {tempo_total:<15} | {processo.tempo_pronto:<15} | {processo.tempo_bloqueado:<15} | {processo.tempo_executando:<10}")
        print("=" * 80)

    def _executar(self):
        processos_aguardando = self.gerenciador.todos_processos.copy()
        
        while (processos_aguardando or self.processos_prontos or 
               self.processos_executando or self.processos_bloqueados):
            
            # 1. Chegada de novos processos
            processos_chegaram = [p for p in processos_aguardando if p.tempo_criacao <= self.gerenciador.clock]
            for p in processos_chegaram:
                print(f"\nClock {self.gerenciador.clock}: Processo {p.pid} chegou ao sistema (PRONTO)")
                processos_aguardando.remove(p)
                self.processos_prontos.append(p)
            
            # 2. Processar decremento de tempo de E/S
            if self.operacoes_es_ativas:
                self.processar_operacoes_es()
            
            # 3. Escalonar próximo processo se a CPU estiver livre
            if not self.processos_executando and self.processos_prontos:
                proximo = self.processos_prontos.pop(0)
                proximo.estado = 'executando'
                self.processos_executando.append(proximo)
                proximo.instante_inicio_cpu = self.gerenciador.clock
                
                # Inicializa o gerenciador de memória para este processo
                if proximo.pid not in self.dict_process_mem:
                    mem_ger = processMemGerenciador(proximo)
                    mem_ger.politica_mem = self.gerenciador.politica_memoria
                    self.dict_process_mem[proximo.pid] = mem_ger
                
                print(f"\nClock {self.gerenciador.clock}: Processo {proximo.pid} recebeu a CPU")
            
            # 4. Exibir estado do sistema
            self.exibir_estado_sistema()
            
            # 5. Executar o processo atual (respeitando o quantum/fatia de CPU)
            if self.processos_executando:
                proc_atual = self.processos_executando[0]
                
                # O tempo de execução nesta fatia é o menor entre o tempo restante do processo e o quantum
                tempo_fatia = min(proc_atual.tempo_execucao_restante, self.fracao_cpu)
                
                # Verifica se haverá requisição de E/S durante esta fatia
                disp_es, momento_req = self.verificar_requisicao_es(proc_atual)
                
                if disp_es is not None and momento_req >= 0 and momento_req < tempo_fatia:
                    # O processo executa até o momento da requisição de E/S
                    print(f"\nClock {self.gerenciador.clock}: Processo {proc_atual.pid} executou por {momento_req} unidades e solicitou E/S")
                    
                    # Avança a memória para cada tick executado antes da E/S
                    for _ in range(momento_req):
                        self.dict_process_mem[proc_atual.pid].main_call()
                        
                    proc_atual.tempo_execucao_restante -= momento_req
                    proc_atual.tempo_executando += momento_req
                    self.gerenciador.clock += momento_req
                    
                    self.solicitar_es(proc_atual, disp_es)
                else:
                    # O processo executa a fatia inteira (ou até terminar, se o tempo restante for menor que o quantum)
                    print(f"\nClock {self.gerenciador.clock}: Processo {proc_atual.pid} executando por {tempo_fatia} unidades")
                    
                    # Avança a memória para cada tick da fatia completa
                    for _ in range(tempo_fatia):
                        self.dict_process_mem[proc_atual.pid].main_call()
                        
                    proc_atual.tempo_execucao_restante -= tempo_fatia
                    proc_atual.tempo_executando += tempo_fatia
                    self.gerenciador.clock += tempo_fatia
                    
                    if proc_atual.tempo_execucao_restante <= 0:
                        # Processo terminou sua execução total
                        proc_atual.instante_conclusao = self.gerenciador.clock
                        proc_atual.estado = 'concluido'
                        print(f"\nClock {self.gerenciador.clock}: Processo {proc_atual.pid} TERMINOU")
                        self.processos_executando.remove(proc_atual)
                    else:
                        # Processo esgotou o quantum, volta para o final da fila de prontos
                        proc_atual.estado = 'pronto'
                        self.processos_executando.remove(proc_atual)
                        self.processos_prontos.append(proc_atual)
                        print(f"\nClock {self.gerenciador.clock}: Processo {proc_atual.pid} esgotou fatia de CPU (volta para PRONTO)")
            
            # 6. Atualizar contadores de espera
            self.atualizar_tempos_espera()
            
            # Pausa para visualização no terminal
            t.sleep(self.sleep_time)
        
        self.exibir_estatisticas_finais()
