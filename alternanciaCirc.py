import time as t

class AlternanciaCirc:
    def __init__(self, gerenciador):
        self.gerenciador = gerenciador
        # Usar processosAtivos para os que estão rodando
        self.processos = gerenciador.processosAtivos
        self.processosFuturos = gerenciador.processosFuturos
        self.processosProntos = gerenciador.processoPronto
        self.generalSleepTime = 0.003

    def iniciar(self):
        self._alternanciaCirc()

    def _alternanciaCirc(self):
        while len(self.processos) > 0 or len(self.processosFuturos) > 0:
            # Trazer processos que chegaram
            novos = [p for p in self.processosFuturos if p.startTime <= self.gerenciador.clock]
            for p in novos:
                self.processos.append(p)
                self.processosFuturos.remove(p)

            if not self.processos:
                self.gerenciador.clock += 1
                continue

            # Executa o primeiro da fila circular
            proc = self.processos[0]
            proc.runtimeResumedAt.append(self.gerenciador.clock)
            print(f"\u2b06 Processo {proc.PiD} recebe a CPU...\n")
            t.sleep(self.generalSleepTime)

            # Executa por até uma fração de CPU
            tempo_exec = min(proc.execTime, self.gerenciador.fracaoCPU)
            proc.execTime -= tempo_exec
            self.gerenciador.clock += tempo_exec
            print(f"⬆ Processo {proc.PiD} na CPU. Tempo restante: {proc.execTime} unidades.\n")
            proc.stopedRuntimeAt.append(self.gerenciador.clock)

            if proc.execTime == 0:
                proc.instanteConclusao = self.gerenciador.clock
                print(f"\u2705 Processo {proc.PiD} terminou\n")
                t.sleep(self.generalSleepTime)
                self.processosProntos.append(proc)
                self.processos.pop(0)
            else:
                print(f"\u274C Processo {proc.PiD} saiu da CPU...\n")
                t.sleep(self.generalSleepTime)
                # Round-robin: move para o final
                self.processos.append(self.processos.pop(0))